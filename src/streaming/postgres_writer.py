import os
from pathlib import Path
from datetime import datetime

import joblib
import pandas as pd
import psycopg2

from src.database.redis_client import (
    cache_transaction,
    add_recent_transaction,
)


# --------------------------------------------------
# Database configuration
# --------------------------------------------------

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "5433")),
    "database": os.getenv("DB_NAME", "streampulse"),
    "user": os.getenv("DB_USER", "streampulse"),
    "password": os.getenv(
        "DB_PASSWORD",
        "streampulse_password"
    ),
}


# --------------------------------------------------
# Load ML model
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "fraud_model.pkl"
)

model_bundle = joblib.load(MODEL_PATH)

if isinstance(model_bundle, dict):
    model = model_bundle["model"]
else:
    model = model_bundle


# --------------------------------------------------
# Save Spark batch
# --------------------------------------------------

def save_batch(batch_df, batch_id):

    print(
        f"\nProcessing Spark batch: {batch_id}"
    )

    if batch_df.isEmpty():
        print("No transactions in this batch.")
        return

    pdf = batch_df.toPandas()

    # --------------------------------------------------
    # ML prediction
    # --------------------------------------------------

    features = pdf[
        [
            "amount",
            "unknown_device",
            "online_payment",
            "unusual_location",
        ]
    ]

    predictions = model.predict(features)

    probabilities = (
        model.predict_proba(features)[:, 1]
    )

    pdf["fraud_prediction"] = (
        predictions.astype(int)
    )

    pdf["fraud_probability"] = probabilities

    # --------------------------------------------------
    # Risk level
    # --------------------------------------------------

    def calculate_risk(probability):

        if probability >= 0.80:
            return "HIGH"

        elif probability >= 0.50:
            return "MEDIUM"

        return "LOW"

    pdf["risk_level"] = (
        pdf["fraud_probability"]
        .apply(calculate_risk)
    )

    # --------------------------------------------------
    # PostgreSQL connection
    # --------------------------------------------------

    print(
        f"Connecting to PostgreSQL: "
        f"{DB_CONFIG['host']}:{DB_CONFIG['port']}"
    )

    connection = psycopg2.connect(
        **DB_CONFIG
    )

    cursor = connection.cursor()

    query = """
    INSERT INTO transactions (
        transaction_id,
        customer_id,
        amount,
        location,
        merchant,
        payment_method,
        device,
        transaction_timestamp,
        fraud_prediction,
        fraud_probability,
        risk_score,
        risk_level
    )
    VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s
    )
    ON CONFLICT (transaction_id)
    DO NOTHING;
    """

    # --------------------------------------------------
    # Write transactions
    # --------------------------------------------------

    for _, row in pdf.iterrows():

        timestamp = row["timestamp"]

        try:

            timestamp = datetime.fromisoformat(
                str(timestamp).replace(
                    "Z",
                    "+00:00"
                )
            )

        except ValueError:

            timestamp = None

        transaction = {

            "transaction_id":
                row["transaction_id"],

            "customer_id":
                row["customer_id"],

            "amount":
                float(row["amount"]),

            "location":
                row["location"],

            "merchant":
                row["merchant"],

            "payment_method":
                row["payment_method"],

            "device":
                row["device"],

            "timestamp":
                str(row["timestamp"]),

            "fraud_prediction":
                int(row["fraud_prediction"]),

            "fraud_probability":
                float(row["fraud_probability"]),

            "risk_score":
                int(row["risk_score"]),

            "risk_level":
                row["risk_level"],
        }

        cursor.execute(
            query,
            (
                transaction["transaction_id"],
                transaction["customer_id"],
                transaction["amount"],
                transaction["location"],
                transaction["merchant"],
                transaction["payment_method"],
                transaction["device"],
                timestamp,
                transaction["fraud_prediction"],
                transaction["fraud_probability"],
                transaction["risk_score"],
                transaction["risk_level"],
            ),
        )

        # --------------------------------------------------
        # Redis cache
        # --------------------------------------------------

        try:

            cache_transaction(
                transaction
            )

            add_recent_transaction(
                transaction
            )

        except Exception as redis_error:

            print(
                f"Redis warning: {redis_error}"
            )

    connection.commit()

    cursor.close()
    connection.close()

    # --------------------------------------------------
    # Batch summary
    # --------------------------------------------------

    print(
        f"Saved {len(pdf)} transactions "
        f"to PostgreSQL."
    )

    print(
        f"Cached {len(pdf)} transactions "
        f"in Redis."
    )

    for _, row in pdf.iterrows():

        print(
            f"Transaction: "
            f"{row['transaction_id'][:8]} | "
            f"Prediction: "
            f"{row['fraud_prediction']} | "
            f"Probability: "
            f"{row['fraud_probability']:.4f} | "
            f"Risk: "
            f"{row['risk_level']}"
        )