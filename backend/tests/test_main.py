from fastapi import status

def test_read_main(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Telco Churn Prediction API (Modularized)"}
