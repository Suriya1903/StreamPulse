import joblib


# Load trained model
model = joblib.load("models/fraud_model.pkl")


def predict_fraud(
    amount,
    unknown_device,
    online_payment,
    unusual_location
):
    features = [[
        amount,
        unknown_device,
        online_payment,
        unusual_location
    ]]

    prediction = model.predict(features)[0]

    probability = model.predict_proba(features)[0][1]

    return prediction, probability


# -----------------------------------------
# Test transaction
# -----------------------------------------

prediction, probability = predict_fraud(
    amount=1500,
    unknown_device=0,
    online_payment=0,
    unusual_location=0
)


print("Fraud Prediction:", prediction)
print("Fraud Probability:", probability)