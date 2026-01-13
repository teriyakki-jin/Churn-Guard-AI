from fastapi import APIRouter, Depends, HTTPException
from models import CustomerData
from services import ChurnService
from auth import User, get_current_user

router = APIRouter()
service = ChurnService()

@router.get("/stats")
def get_stats(current_user: User = Depends(get_current_user)):
    return service.get_stats()

@router.get("/analysis")
def get_analysis(current_user: User = Depends(get_current_user)):
    try:
        return service.get_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict")
def predict_churn(data: CustomerData, current_user: User = Depends(get_current_user)):
    try:
        prob = service.predict(data.dict())
        
        input_dict = data.dict()
        suggestions = []
        if input_dict['Contract'] == 'Month-to-month':
            suggestions.append("Offer 1-year contract discount to reduce churn risk (3.7x lower risk).")
        if input_dict['PaymentMethod'] == 'Electronic check':
            suggestions.append("Promote Automatic Payment (Credit Card/Bank Transfer) with a small credit.")
        if input_dict['InternetService'] == 'Fiber optic':
            suggestions.append("Check service stability; Fiber users churn 2.2x more than DSL.")
        if input_dict['MonthlyCharges'] > 70:
            suggestions.append("High monthly bill detected. Offer a bundled data package or loyalty discount.")
        
        if not suggestions:
            suggestions.append("Regular engagement and periodic health checks recommended.")

        return {
            "churn_risk_score": prob,
            "prediction": "Yes" if prob > 0.5 else "No",
            "suggestions": suggestions,
            "summary": "High Risk" if prob > 0.6 else ("Moderate Risk" if prob > 0.3 else "Low Risk")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
