"""
Prediction API v2 - Enhanced with OpenAPI Documentation
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

from models import CustomerData
from services_v2 import ChurnServiceV2
from auth import User, get_current_user
from starlette.requests import Request
from limiter import limiter
from logger import logger
from exceptions import PredictionError

router = APIRouter()
service = ChurnServiceV2()


# ============== Response Models for Documentation ==============

class RiskFactor(BaseModel):
    """Individual risk factor contributing to churn prediction."""
    factor: str = Field(..., description="Name of the risk factor")
    impact: str = Field(..., description="Impact level: high, medium, or low")
    description: str = Field(..., description="Explanation of the risk factor")

    class Config:
        json_schema_extra = {
            "example": {
                "factor": "Month-to-month Contract",
                "impact": "high",
                "description": "3.7x higher churn rate than 2-year contracts"
            }
        }


class RetentionSuggestion(BaseModel):
    """Actionable suggestion for customer retention."""
    action: str = Field(..., description="Recommended action")
    priority: str = Field(..., description="Priority level: high, medium, or low")
    details: str = Field(..., description="Detailed recommendation")
    expected_impact: str = Field(..., description="Expected outcome of the action")

    class Config:
        json_schema_extra = {
            "example": {
                "action": "Offer Contract Upgrade",
                "priority": "high",
                "details": "Provide 15-20% discount for 1-year contract commitment",
                "expected_impact": "Reduce churn risk by 70%"
            }
        }


class PredictionResponse(BaseModel):
    """Complete churn prediction response with analysis."""
    churn_risk_score: float = Field(..., ge=0, le=1, description="Probability of churn (0-1)")
    prediction: str = Field(..., description="Yes or No prediction")
    summary: str = Field(..., description="Risk level summary")
    confidence: float = Field(..., ge=0, le=1, description="Model confidence score")
    risk_factors: List[RiskFactor] = Field(..., description="Contributing risk factors")
    suggestions: List[RetentionSuggestion] = Field(..., description="Retention recommendations")
    model_version: str = Field(..., description="Model version used for prediction")

    class Config:
        json_schema_extra = {
            "example": {
                "churn_risk_score": 0.7234,
                "prediction": "Yes",
                "summary": "High Risk",
                "confidence": 0.4468,
                "risk_factors": [
                    {
                        "factor": "Month-to-month Contract",
                        "impact": "high",
                        "description": "3.7x higher churn rate than 2-year contracts"
                    }
                ],
                "suggestions": [
                    {
                        "action": "Offer Contract Upgrade",
                        "priority": "high",
                        "details": "Provide 15-20% discount for 1-year contract commitment",
                        "expected_impact": "Reduce churn risk by 70%"
                    }
                ],
                "model_version": "v2"
            }
        }


class StatsResponse(BaseModel):
    """Overall churn statistics response."""
    overall_churn_rate: Dict[str, float] = Field(..., description="Overall Yes/No churn rates")
    contract_impact: Dict[str, float] = Field(..., description="Churn rate by contract type")
    payment_impact: Dict[str, float] = Field(..., description="Churn rate by payment method")
    internet_impact: Dict[str, float] = Field(..., description="Churn rate by internet service")
    total_customers: int = Field(..., description="Total number of customers")
    churned_customers: int = Field(..., description="Number of churned customers")
    feature_importance: Dict[str, float] = Field(..., description="Top feature importances")
    model_version: str = Field(..., description="Current model version")
    model_metrics: Optional[Dict[str, float]] = Field(None, description="Model performance metrics")


class StatisticalTest(BaseModel):
    """Statistical test result."""
    variable: str
    test: str
    p_value: float
    significant: bool
    chi2_statistic: Optional[float] = None
    statistic: Optional[float] = None


class SegmentAnalysis(BaseModel):
    """Customer segment analysis."""
    segment: str
    churn_rate: float
    size: int
    pct_of_total: float


class FinancialImpact(BaseModel):
    """Financial impact analysis."""
    avg_monthly_loss: float
    avg_annual_loss_per_customer: float
    total_annual_exposure: float
    avg_customer_lifetime_months: float
    retention_cost_estimate: float
    roi_per_saved_customer: float


class AnalysisResponse(BaseModel):
    """Comprehensive churn analysis response."""
    statistical_tests: List[StatisticalTest]
    segments: List[SegmentAnalysis]
    financial_impact: FinancialImpact
    model_version: str


# ============== API Endpoints ==============

@router.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Predict Customer Churn",
    description="""
    Predicts the probability of customer churn based on their profile data.

    **Features:**
    - Returns churn probability score (0-1)
    - Identifies key risk factors
    - Provides actionable retention suggestions
    - Uses ensemble model (XGBoost + RandomForest + GradientBoosting)

    **Risk Levels:**
    - Critical Risk: >70%
    - High Risk: 50-70%
    - Moderate Risk: 30-50%
    - Low Risk: 15-30%
    - Minimal Risk: <15%
    """,
    response_description="Churn prediction with risk factors and suggestions",
    tags=["Prediction"]
)
@limiter.limit("20/minute")
async def predict_churn(
    request: Request,
    data: CustomerData,
    current_user: User = Depends(get_current_user)
):
    """
    ## Predict Customer Churn

    Analyzes customer data to predict churn probability and provides
    actionable insights for retention.

    ### Input Fields:
    - **gender**: Male or Female
    - **SeniorCitizen**: 0 or 1
    - **Partner**: Yes or No
    - **Dependents**: Yes or No
    - **tenure**: Months as customer (0-72)
    - **PhoneService**: Yes or No
    - **MultipleLines**: Yes, No, or No phone service
    - **InternetService**: DSL, Fiber optic, or No
    - **OnlineSecurity**: Yes, No, or No internet service
    - **OnlineBackup**: Yes, No, or No internet service
    - **DeviceProtection**: Yes, No, or No internet service
    - **TechSupport**: Yes, No, or No internet service
    - **StreamingTV**: Yes, No, or No internet service
    - **StreamingMovies**: Yes, No, or No internet service
    - **Contract**: Month-to-month, One year, or Two year
    - **PaperlessBilling**: Yes or No
    - **PaymentMethod**: Electronic check, Mailed check, Bank transfer, Credit card
    - **MonthlyCharges**: Monthly charge amount
    - **TotalCharges**: Total charges to date

    ### Returns:
    - Churn probability score
    - Risk factors analysis
    - Retention suggestions
    """
    try:
        result = service.predict(data.dict())
        logger.info(f"Churn prediction for user {current_user.username}: {result['prediction']} (Score: {result['churn_risk_score']:.4f})")
        return result
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        # If it's already a ChurnException, re-raise it
        if hasattr(e, 'status_code'):
             raise e
        # Otherwise wrap in PredictionError for this endpoint
        raise PredictionError(f"Failed to process prediction: {str(e)}")


@router.get(
    "/stats",
    response_model=StatsResponse,
    summary="Get Churn Statistics",
    description="""
    Returns comprehensive churn statistics and insights.

    **Includes:**
    - Overall churn rate
    - Churn rate by contract type
    - Churn rate by payment method
    - Churn rate by internet service
    - Feature importance scores
    - Model performance metrics
    """,
    tags=["Analytics"]
)
async def get_stats(current_user: User = Depends(get_current_user)):
    """
    ## Get Churn Statistics

    Retrieves overall churn metrics and breakdown by key factors.
    """
    try:
        return service.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/analysis",
    response_model=AnalysisResponse,
    summary="Get Detailed Analysis",
    description="""
    Returns detailed statistical analysis of churn factors.

    **Analysis Components:**
    1. **Statistical Tests**: Chi-square and Mann-Whitney U tests
    2. **Segment Analysis**: High-risk customer segments
    3. **Financial Impact**: Revenue exposure and ROI calculations
    """,
    tags=["Analytics"]
)
async def get_analysis(current_user: User = Depends(get_current_user)):
    """
    ## Get Detailed Churn Analysis

    Comprehensive statistical analysis including:
    - Significance tests for categorical and numerical variables
    - High-risk segment identification
    - Financial impact modeling
    """
    try:
        return service.get_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/model-info",
    summary="Get Model Information",
    description="Returns information about the current prediction model.",
    tags=["Model"]
)
async def get_model_info(current_user: User = Depends(get_current_user)):
    """
    ## Get Model Information

    Returns metadata about the current prediction model including
    version, performance metrics, and training details.
    """
    return {
        "version": service.model_version,
        "type": "Ensemble (XGBoost + RandomForest + GradientBoosting)",
        "metadata": service.metadata,
        "feature_count": len(service.feature_names) if service.feature_names else 0
    }
