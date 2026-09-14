from pathlib import Path

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "fraud_model.pkl"
)


FEATURES = [
    "amount",
    "unknown_device",
    "online_payment",
    "unusual_location",
]


def load_model():

    model_bundle = joblib.load(
        MODEL_PATH
    )

    if isinstance(model_bundle, dict):
        return model_bundle["model"]

    return model_bundle


def create_features(
    amount,
    unknown_device,
    online_payment,
    unusual_location,
):

    return pd.DataFrame(
        [[
            amount,
            unknown_device,
            online_payment,
            unusual_location,
        ]],
        columns=FEATURES,
    )


def test_model_file_exists():

    assert MODEL_PATH.exists()


def test_model_can_predict():

    model = load_model()

    features = create_features(
        amount=2500,
        unknown_device=0,
        online_payment=0,
        unusual_location=0,
    )

    prediction = model.predict(
        features
    )

    assert len(prediction) == 1


def test_model_probability_is_valid():

    model = load_model()

    features = create_features(
        amount=2500,
        unknown_device=0,
        online_payment=0,
        unusual_location=0,
    )

    probability = (
        model.predict_proba(features)[0][1]
    )

    assert 0 <= probability <= 1


def test_suspicious_transaction():

    model = load_model()

    features = create_features(
        amount=100000,
        unknown_device=1,
        online_payment=1,
        unusual_location=1,
    )

    prediction = model.predict(
        features
    )[0]

    probability = (
        model.predict_proba(features)[0][1]
    )

    assert prediction in [0, 1]

    assert 0 <= probability <= 1