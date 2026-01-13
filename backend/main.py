from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, prediction

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(prediction.router)

@app.get("/")
def read_root():
    return {"message": "Telco Churn Prediction API (Modularized)"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

