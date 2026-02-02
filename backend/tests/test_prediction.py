"""Prediction API tests."""
from fastapi import status
from db_models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# High-risk customer: Month-to-month contract, Electronic check, short tenure
HIGH_RISK_CUSTOMER = {
    "gender": "Male",
    "SeniorCitizen": 0,
    "Partner": "No",
    "Dependents": "No",
    "tenure": 2,
    "PhoneService": "Yes",
    "MultipleLines": "No",
    "InternetService": "Fiber optic",
    "OnlineSecurity": "No",
    "OnlineBackup": "No",
    "DeviceProtection": "No",
    "TechSupport": "No",
    "StreamingTV": "No",
    "StreamingMovies": "No",
    "Contract": "Month-to-month",
    "PaperlessBilling": "Yes",
    "PaymentMethod": "Electronic check",
    "MonthlyCharges": 85.0,
    "TotalCharges": 170.0
}

# Low-risk customer: Two year contract, automatic payment, long tenure
LOW_RISK_CUSTOMER = {
    "gender": "Female",
    "SeniorCitizen": 0,
    "Partner": "Yes",
    "Dependents": "Yes",
    "tenure": 48,
    "PhoneService": "Yes",
    "MultipleLines": "Yes",
    "InternetService": "DSL",
    "OnlineSecurity": "Yes",
    "OnlineBackup": "Yes",
    "DeviceProtection": "Yes",
    "TechSupport": "Yes",
    "StreamingTV": "Yes",
    "StreamingMovies": "Yes",
    "Contract": "Two year",
    "PaperlessBilling": "No",
    "PaymentMethod": "Credit card (automatic)",
    "MonthlyCharges": 65.0,
    "TotalCharges": 3120.0
}


def get_auth_token(client, db_session):
    """Helper to create user and get auth token."""
    hashed_password = pwd_context.hash("testpass")
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hashed_password,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/token",
        data={"username": "testuser", "password": "testpass"}
    )
    return response.json()["access_token"]


def test_predict_high_risk(client, db_session):
    """Test prediction for high-risk customer."""
    token = get_auth_token(client, db_session)

    response = client.post(
        "/api/predict",
        json=HIGH_RISK_CUSTOMER,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "churn_risk_score" in data
    assert "prediction" in data
    assert "suggestions" in data
    assert "summary" in data

    # High-risk customer should have higher churn probability
    assert data["churn_risk_score"] > 0.4
    assert data["summary"] in ["High Risk", "Moderate Risk"]


def test_predict_low_risk(client, db_session):
    """Test prediction for low-risk customer."""
    token = get_auth_token(client, db_session)

    response = client.post(
        "/api/predict",
        json=LOW_RISK_CUSTOMER,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # Low-risk customer should have lower churn probability
    assert data["churn_risk_score"] < 0.4
    assert data["summary"] == "Low Risk"


def test_predict_unauthorized(client):
    """Test prediction without authentication."""
    response = client.post("/api/predict", json=HIGH_RISK_CUSTOMER)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_predict_invalid_data(client, db_session):
    """Test prediction with invalid data."""
    token = get_auth_token(client, db_session)

    invalid_data = {"gender": "Male"}  # Missing required fields

    response = client.post(
        "/api/predict",
        json=invalid_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_stats(client, db_session):
    """Test stats endpoint."""
    token = get_auth_token(client, db_session)

    response = client.get(
        "/api/stats",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "overall_churn_rate" in data
    assert "total_customers" in data
    assert "contract_impact" in data
    assert "payment_impact" in data


def test_get_stats_unauthorized(client):
    """Test stats endpoint without authentication."""
    response = client.get("/api/stats")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_analysis(client, db_session):
    """Test analysis endpoint."""
    token = get_auth_token(client, db_session)

    response = client.get(
        "/api/analysis",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # Analysis should return some data structure
    assert isinstance(data, dict)


def test_prediction_suggestions_contract(client, db_session):
    """Test that month-to-month contract triggers suggestion."""
    token = get_auth_token(client, db_session)

    response = client.post(
        "/api/predict",
        json=HIGH_RISK_CUSTOMER,
        headers={"Authorization": f"Bearer {token}"}
    )

    data = response.json()
    suggestions_text = " ".join(data["suggestions"])

    # Should suggest contract upgrade for month-to-month
    assert "contract" in suggestions_text.lower() or "1-year" in suggestions_text


def test_prediction_suggestions_payment(client, db_session):
    """Test that electronic check triggers suggestion."""
    token = get_auth_token(client, db_session)

    response = client.post(
        "/api/predict",
        json=HIGH_RISK_CUSTOMER,
        headers={"Authorization": f"Bearer {token}"}
    )

    data = response.json()
    suggestions_text = " ".join(data["suggestions"])

    # Should suggest automatic payment for electronic check
    assert "payment" in suggestions_text.lower() or "automatic" in suggestions_text.lower()
