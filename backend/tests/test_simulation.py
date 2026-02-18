from fastapi import status
from unittest.mock import patch
from simulation import ChurnSimulator
from db_models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _patch_ws_session(db_session):
    """Return a context manager that patches SessionLocal in the simulation router."""
    class _FakeSessionLocal:
        def __init__(self):
            self._session = db_session

        def __call__(self):
            return self._session

        def close(self):
            pass  # managed by fixture

    fake = _FakeSessionLocal()
    return patch("routers.simulation.SessionLocal", fake)


# Helper to create a user and get token

def get_auth_token(client, db_session):
    user = db_session.query(User).filter(User.username == "sim_tester").first()
    if not user:
        hashed_password = pwd_context.hash("testpass")
        user = User(
            username="sim_tester",
            email="sim@example.com",
            hashed_password=hashed_password,
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

    response = client.post("/api/token", data={"username": "sim_tester", "password": "testpass"})
    return response.json()["access_token"]


def get_auth_headers(client, db_session):
    token = get_auth_token(client, db_session)
    return {"Authorization": f"Bearer {token}"}


def test_simulator_logic():
    sim = ChurnSimulator(seed=42)
    customer = sim.generate_customer()

    assert "customer_id" in customer
    assert "tenure" in customer
    assert customer["customer_id"].startswith("SIM-")

    profile = customer["_profile"]
    if profile == "high_risk":
        assert customer["Contract"] == "Month-to-month"


def test_simulation_batch_unauthorized(client):
    response = client.get("/api/simulation/batch")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_simulation_batch(client, db_session):
    headers = get_auth_headers(client, db_session)
    response = client.get("/api/simulation/batch?count=5", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "summary" in data
    assert "customers" in data
    assert len(data["customers"]) == 5
    assert data["summary"]["total"] == 5

    first_customer = data["customers"][0]
    assert "churn_probability" in first_customer
    assert "risk_level" in first_customer


def test_simulation_stats(client, db_session):
    headers = get_auth_headers(client, db_session)
    response = client.get("/api/simulation/stats", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "active_connections" in data
    assert "simulator_customer_count" in data


def test_simulation_websocket(client, db_session):
    token = get_auth_token(client, db_session)

    with _patch_ws_session(db_session):
        with client.websocket_connect(f"/api/ws/simulation?interval=0.5&token={token}") as websocket:
            data = websocket.receive_json()

            assert data["type"] == "prediction"
            assert "customer_id" in data
            assert "prediction" in data
            assert data["prediction"]["churn_probability"] >= 0

            data2 = websocket.receive_json()
            assert data2["type"] == "prediction"
            assert data["customer_id"] != data2["customer_id"]
