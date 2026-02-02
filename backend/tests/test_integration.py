"""Integration tests for the complete user flow."""
from fastapi import status
from db_models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SAMPLE_CUSTOMER = {
    "gender": "Male",
    "SeniorCitizen": 0,
    "Partner": "No",
    "Dependents": "No",
    "tenure": 12,
    "PhoneService": "Yes",
    "MultipleLines": "No",
    "InternetService": "DSL",
    "OnlineSecurity": "Yes",
    "OnlineBackup": "No",
    "DeviceProtection": "No",
    "TechSupport": "No",
    "StreamingTV": "No",
    "StreamingMovies": "No",
    "Contract": "One year",
    "PaperlessBilling": "Yes",
    "PaymentMethod": "Bank transfer (automatic)",
    "MonthlyCharges": 55.0,
    "TotalCharges": 660.0
}


class TestUserFlow:
    """Test complete user workflow: register -> login -> predict."""

    def test_complete_flow(self, client, db_session):
        """Test the complete user flow from login to prediction."""
        # Step 1: Create user in DB (simulating registration)
        hashed_password = pwd_context.hash("securepass123")
        user = User(
            username="flowuser",
            email="flow@example.com",
            hashed_password=hashed_password,
            is_active=True
        )
        db_session.add(user)
        db_session.commit()

        # Step 2: Login
        login_response = client.post(
            "/api/token",
            data={"username": "flowuser", "password": "securepass123"}
        )
        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Step 3: Get stats
        stats_response = client.get("/api/stats", headers=headers)
        assert stats_response.status_code == status.HTTP_200_OK
        stats = stats_response.json()
        assert stats["total_customers"] > 0

        # Step 4: Get analysis
        analysis_response = client.get("/api/analysis", headers=headers)
        assert analysis_response.status_code == status.HTTP_200_OK

        # Step 5: Make prediction
        predict_response = client.post(
            "/api/predict",
            json=SAMPLE_CUSTOMER,
            headers=headers
        )
        assert predict_response.status_code == status.HTTP_200_OK
        prediction = predict_response.json()
        assert 0 <= prediction["churn_risk_score"] <= 1


class TestTokenExpiration:
    """Test token-related scenarios."""

    def test_invalid_token(self, client):
        """Test access with invalid token."""
        headers = {"Authorization": "Bearer invalid_token_here"}

        response = client.get("/api/stats", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_malformed_auth_header(self, client):
        """Test access with malformed authorization header."""
        headers = {"Authorization": "NotBearer token"}

        response = client.get("/api/stats", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestMultipleUsers:
    """Test scenarios with multiple users."""

    def test_different_users_access(self, client, db_session):
        """Test that different users can independently access the system."""
        # Create two users
        for i in range(2):
            user = User(
                username=f"user{i}",
                email=f"user{i}@example.com",
                hashed_password=pwd_context.hash(f"pass{i}"),
                is_active=True
            )
            db_session.add(user)
        db_session.commit()

        # Login as user0
        response0 = client.post(
            "/api/token",
            data={"username": "user0", "password": "pass0"}
        )
        token0 = response0.json()["access_token"]

        # Login as user1
        response1 = client.post(
            "/api/token",
            data={"username": "user1", "password": "pass1"}
        )
        token1 = response1.json()["access_token"]

        # Both should be able to access stats
        stats0 = client.get(
            "/api/stats",
            headers={"Authorization": f"Bearer {token0}"}
        )
        stats1 = client.get(
            "/api/stats",
            headers={"Authorization": f"Bearer {token1}"}
        )

        assert stats0.status_code == status.HTTP_200_OK
        assert stats1.status_code == status.HTTP_200_OK


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_extreme_values(self, client, db_session):
        """Test prediction with extreme values."""
        hashed_password = pwd_context.hash("testpass")
        user = User(
            username="edgeuser",
            email="edge@example.com",
            hashed_password=hashed_password,
            is_active=True
        )
        db_session.add(user)
        db_session.commit()

        response = client.post(
            "/api/token",
            data={"username": "edgeuser", "password": "testpass"}
        )
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Customer with maximum tenure and charges
        extreme_customer = {
            "gender": "Female",
            "SeniorCitizen": 1,
            "Partner": "Yes",
            "Dependents": "Yes",
            "tenure": 72,  # Max tenure
            "PhoneService": "Yes",
            "MultipleLines": "Yes",
            "InternetService": "Fiber optic",
            "OnlineSecurity": "Yes",
            "OnlineBackup": "Yes",
            "DeviceProtection": "Yes",
            "TechSupport": "Yes",
            "StreamingTV": "Yes",
            "StreamingMovies": "Yes",
            "Contract": "Two year",
            "PaperlessBilling": "No",
            "PaymentMethod": "Credit card (automatic)",
            "MonthlyCharges": 118.75,  # High charges
            "TotalCharges": 8550.0
        }

        response = client.post(
            "/api/predict",
            json=extreme_customer,
            headers=headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 0 <= data["churn_risk_score"] <= 1

    def test_zero_tenure(self, client, db_session):
        """Test prediction for brand new customer (tenure=0)."""
        hashed_password = pwd_context.hash("testpass")
        user = User(
            username="newuser",
            email="new@example.com",
            hashed_password=hashed_password,
            is_active=True
        )
        db_session.add(user)
        db_session.commit()

        response = client.post(
            "/api/token",
            data={"username": "newuser", "password": "testpass"}
        )
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        new_customer = {
            "gender": "Male",
            "SeniorCitizen": 0,
            "Partner": "No",
            "Dependents": "No",
            "tenure": 0,  # Brand new
            "PhoneService": "Yes",
            "MultipleLines": "No",
            "InternetService": "DSL",
            "OnlineSecurity": "No",
            "OnlineBackup": "No",
            "DeviceProtection": "No",
            "TechSupport": "No",
            "StreamingTV": "No",
            "StreamingMovies": "No",
            "Contract": "Month-to-month",
            "PaperlessBilling": "Yes",
            "PaymentMethod": "Electronic check",
            "MonthlyCharges": 29.85,
            "TotalCharges": 0.0
        }

        response = client.post(
            "/api/predict",
            json=new_customer,
            headers=headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # New customers with month-to-month should be higher risk
        assert data["churn_risk_score"] >= 0
