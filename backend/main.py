from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth
from routers.prediction_v2 import router as prediction_router
from routers.simulation import router as simulation_router
from routers import reports, notifications
from database import init_db

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request
from limiter import limiter
from logger import logger
import time
import os

init_db()

# API Metadata
app = FastAPI(
    title="Churn Guard AI API",
    description="""
## Customer Churn Prediction API

Churn Guard AI provides machine learning-powered customer churn prediction
with actionable retention insights.

### Features
- **Churn Prediction**: Predict customer churn probability with ensemble ML models
- **Risk Analysis**: Identify key risk factors for each customer
- **Retention Suggestions**: Get actionable recommendations to reduce churn
- **Analytics**: Comprehensive statistics and segment analysis
- **Financial Impact**: ROI calculations for retention strategies

### Model
- **Type**: Voting Ensemble (XGBoost + RandomForest + GradientBoosting)
- **Performance**: ~84% accuracy, 0.88 ROC-AUC
- **Features**: 50+ engineered features including customer value scores

### Authentication
All endpoints require JWT Bearer token authentication.
    """,
    version="2.0.0",
    terms_of_service="https://github.com/teriyakki-jin/Churn-Guard-AI",
    contact={
        "name": "Churn Guard AI Support",
        "url": "https://github.com/teriyakki-jin/Churn-Guard-AI",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {"name": "Authentication", "description": "User authentication and token management"},
        {"name": "Prediction", "description": "Customer churn prediction endpoints"},
        {"name": "Analytics", "description": "Statistics and analysis endpoints"},
        {"name": "Model", "description": "Model information and metadata"},
        {"name": "Simulation", "description": "Real-time customer simulation and streaming predictions"},
    ]
)

# Set up Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

from exceptions import ChurnException, churn_exception_handler, generic_exception_handler
app.add_exception_handler(ChurnException, churn_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"
    response.headers["Cache-Control"] = "no-store"

    logger.info(
        f"Path: {request.url.path} Method: {request.method} "
        f"Status: {response.status_code} Duration: {process_time:.4f}s"
    )
    return response


# CORS allow-list via env (comma-separated)
raw_origins = os.getenv("CORS_ALLOW_ORIGINS")
if raw_origins:
    cors_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]
elif os.getenv("FRONTEND_URL"):
    cors_origins = [os.getenv("FRONTEND_URL")]
else:
    cors_origins = ["http://localhost:5173", "http://localhost:5174"]

allow_credentials = not (len(cors_origins) == 1 and cors_origins[0] == "*")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=allow_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

app.include_router(auth.router, prefix="/api", tags=["Authentication"])
app.include_router(prediction_router, prefix="/api")
app.include_router(simulation_router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")


@app.get("/", tags=["Health"])
def read_root():
    return {
        "message": "Churn Guard AI API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
