from fastapi.testclient import TestClient
from fastapi import status
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app
from unittest.mock import MagicMock, patch
import pytest
from db_models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_auth_headers(client, db_session):
    user = db_session.query(User).filter(User.username == "report_tester").first()
    if not user:
        hashed_password = pwd_context.hash("testpass")
        user = User(username="report_tester", email="rep@example.com", hashed_password=hashed_password, is_active=True)
        db_session.add(user)
        db_session.commit()
    
    response = client.post("/api/token", data={"username": "report_tester", "password": "testpass"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_export_csv(client, db_session):
    """Test CSV export."""
    headers = get_auth_headers(client, db_session)
    response = client.get("/api/reports/export/csv", headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"].startswith("text/csv")
    assert "Average Monthly Charges" not in response.text # Should use keys from flattened stats

def test_export_pdf(client, db_session):
    """Test PDF export."""
    headers = get_auth_headers(client, db_session)
    response = client.get("/api/reports/export/pdf", headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "application/pdf"
    assert len(response.content) > 0 # Ensure PDF is not empty

@patch("routers.notifications.FastMail")
def test_send_report_email(mock_fastmail, client, db_session):
    """Test email sending endpoint (mocked)."""
    from unittest.mock import AsyncMock
    headers = get_auth_headers(client, db_session)

    # send_message is async — must use AsyncMock so `await fm.send_message()` works
    mock_fm_instance = MagicMock()
    mock_fm_instance.send_message = AsyncMock(return_value=None)
    mock_fastmail.return_value = mock_fm_instance
    
    payload = {"email": ["test@example.com"]}
    response = client.post("/api/notifications/send-report", json=payload, headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Email sending queued"
    
    # Background tasks are hard to test synchronously without forcing execution,
    # but status 200 confirms the endpoint logic ran.
