import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
import sys
import os

# Set testing environment variable to disable rate limiting
os.environ["TESTING"] = "true"

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Stub out fastapi_mail before importing the app — the installed version has a
# bug where SecretStr is undefined at import time. Email is not tested here.
_mail_stub = MagicMock()
sys.modules.setdefault("fastapi_mail", _mail_stub)
for _sub in ("fastapi_mail.config", "fastapi_mail.schemas", "fastapi_mail.errors"):
    sys.modules.setdefault(_sub, _mail_stub)

from main import app
from database import get_db
from db_models import Base
from limiter import limiter

# Force disable limiter
limiter.enabled = False

# In-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create a TestClient with overridden database dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Ensure limiter is disabled
    if hasattr(app.state, "limiter"):
        app.state.limiter.enabled = False
        
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
