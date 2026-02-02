from fastapi import status
from db_models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_create_user(db_session):
    """Test user creation directly in DB."""
    hashed_password = pwd_context.hash("testpass")
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hashed_password,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    saved_user = db_session.query(User).filter(User.username == "testuser").first()
    assert saved_user is not None
    assert saved_user.email == "test@example.com"

def test_login_success(client, db_session):
    """Test successful login and token retrieval."""
    # Create user
    hashed_password = pwd_context.hash("testpass")
    user = User(
        username="testuser",
        hashed_password=hashed_password,
        email="test@example.com",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    response = client.post(
        "/api/token",
        data={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_wrong_password(client, db_session):
    """Test login failure with wrong password."""
    hashed_password = pwd_context.hash("testpass")
    user = User(
        username="testuser",
        hashed_password=hashed_password,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    response = client.post(
        "/api/token",
        data={"username": "testuser", "password": "wrongpass"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
