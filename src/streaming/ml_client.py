import requests


API_URL = "http://127.0.0.1:8000/predict"


def predict_transaction(
    amount,
    unknown_device,
    online_payment,
    unusual_location
):

    payload = {
        "amount": float(amount),
        "unknown_device": int(unknown_device),
        "online_payment": int(online_payment),
        "unusual_location": int(unusual_location)
    }

    response = requests.post(
        API_URL,
        json=payload,
        timeout=5
    )

    response.raise_for_status()

    return response.json()