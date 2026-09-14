from fastapi.testclient import TestClient

from src.api.fraud_api import app


client = TestClient(app)


def test_health_endpoint():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"

    assert data["model_loaded"] is True


def test_predict_endpoint():

    response = client.post(
        "/predict",
        json={
            "amount": 2500,
            "unknown_device": 0,
            "online_payment": 0,
            "unusual_location": 0,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "fraud_prediction" in data

    assert "fraud_probability" in data

    assert "risk_level" in data


def test_predict_probability_range():

    response = client.post(
        "/predict",
        json={
            "amount": 100000,
            "unknown_device": 1,
            "online_payment": 1,
            "unusual_location": 1,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        0
        <= data["fraud_probability"]
        <= 1
    )


def test_invalid_prediction_request():

    response = client.post(
        "/predict",
        json={
            "amount": "invalid",
            "unknown_device": 0,
            "online_payment": 0,
            "unusual_location": 0,
        },
    )

    assert response.status_code == 422