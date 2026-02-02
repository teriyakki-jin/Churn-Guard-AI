from fastapi import status

def test_read_main(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Churn Guard AI API"
    assert data["status"] == "running"
