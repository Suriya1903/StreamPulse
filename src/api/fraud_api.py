import os
import pandas as pd
from pathlib import Path

import joblib
import psycopg2

from fastapi import FastAPI
from pydantic import BaseModel

from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Gauge

from src.database.redis_client import (
    get_recent_transactions,
    check_redis_connection,
)


# --------------------------------------------------
# Configuration
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = PROJECT_ROOT / "models" / "fraud_model.pkl"


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

model_bundle = joblib.load(MODEL_PATH)

if isinstance(model_bundle, dict):
    model = model_bundle["model"]
else:
    model = model_bundle


# --------------------------------------------------
# FastAPI
# --------------------------------------------------

app = FastAPI(
    title="StreamPulse Fraud Detection API",
    description="Real-time fraud detection and analytics API",
    version="1.0.0",
)


# --------------------------------------------------
# Prometheus Custom Metrics
# --------------------------------------------------

# Transaction metrics

total_transactions_metric = Gauge(
    "streampulse_total_transactions",
    "Total number of transactions"
)

fraud_transactions_metric = Gauge(
    "streampulse_fraud_transactions",
    "Total number of fraudulent transactions"
)

normal_transactions_metric = Gauge(
    "streampulse_normal_transactions",
    "Total number of normal transactions"
)

fraud_rate_metric = Gauge(
    "streampulse_fraud_rate",
    "Fraud percentage"
)


# Risk metrics

low_risk_transactions_metric = Gauge(
    "streampulse_low_risk_transactions",
    "Number of low risk transactions"
)

medium_risk_transactions_metric = Gauge(
    "streampulse_medium_risk_transactions",
    "Number of medium risk transactions"
)

high_risk_transactions_metric = Gauge(
    "streampulse_high_risk_transactions",
    "Number of high risk transactions"
)


# --------------------------------------------------
# Prometheus HTTP Metrics
# --------------------------------------------------

Instrumentator().instrument(app).expose(app)


# --------------------------------------------------
# Database helper
# --------------------------------------------------

def get_db_connection():

    return psycopg2.connect(**DB_CONFIG)


# --------------------------------------------------
# Request model
# --------------------------------------------------

class Transaction(BaseModel):

    amount: float

    unknown_device: int

    online_payment: int

    unusual_location: int


# --------------------------------------------------
# Health
# --------------------------------------------------

@app.get("/health")
def health_check():

    try:

        redis_status = check_redis_connection()

    except Exception:

        redis_status = False

    return {
        "status": "healthy",
        "service": "fraud-detection-api",
        "model_loaded": True,
        "redis_connected": redis_status,
    }


# --------------------------------------------------
# ML Prediction
# --------------------------------------------------

@app.post("/predict")
def predict_fraud(transaction: Transaction):

    features = pd.DataFrame(
        [[
            transaction.amount,
            transaction.unknown_device,
            transaction.online_payment,
            transaction.unusual_location,
        ]],
        columns=[
            "amount",
            "unknown_device",
            "online_payment",
            "unusual_location",
        ],
    )

    prediction = model.predict(features)[0]

    probability = model.predict_proba(features)[0][1]

    if probability >= 0.80:

        risk_level = "HIGH"

    elif probability >= 0.50:

        risk_level = "MEDIUM"

    else:

        risk_level = "LOW"

    return {
        "fraud_prediction": int(prediction),
        "fraud_probability": round(
            float(probability),
            4
        ),
        "risk_level": risk_level,
    }


# --------------------------------------------------
# Recent Transactions
# --------------------------------------------------

@app.get("/transactions")
def get_transactions(limit: int = 20):

    # --------------------------------------------------
    # Try Redis first
    # --------------------------------------------------

    try:

        cached_transactions = (
            get_recent_transactions(limit)
        )

        if cached_transactions:

            return {
                "count": len(cached_transactions),
                "source": "redis",
                "transactions": cached_transactions,
            }

    except Exception:

        pass


    # --------------------------------------------------
    # Redis unavailable → PostgreSQL fallback
    # --------------------------------------------------

    connection = get_db_connection()

    cursor = connection.cursor()

    query = """
    SELECT
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
    FROM transactions
    ORDER BY id DESC
    LIMIT %s;
    """

    cursor.execute(
        query,
        (limit,)
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    transactions = []

    for row in rows:

        transactions.append({

            "transaction_id": row[0],

            "customer_id": row[1],

            "amount": float(row[2]),

            "location": row[3],

            "merchant": row[4],

            "payment_method": row[5],

            "device": row[6],

            "timestamp": str(row[7]),

            "fraud_prediction": row[8],

            "fraud_probability": float(row[9]),

            "risk_score": row[10],

            "risk_level": row[11],
        })

    return {

        "count": len(transactions),

        "source": "postgresql",

        "transactions": transactions,
    }


# --------------------------------------------------
# Fraud Summary
# --------------------------------------------------

@app.get("/fraud-summary")
def fraud_summary():

    connection = get_db_connection()

    cursor = connection.cursor()

    query = """
    SELECT
        COUNT(*) AS total_transactions,

        COUNT(*) FILTER (
            WHERE fraud_prediction = 1
        ) AS fraudulent_transactions,

        COUNT(*) FILTER (
            WHERE fraud_prediction = 0
        ) AS normal_transactions,

        COALESCE(
            AVG(fraud_probability),
            0
        ) AS average_fraud_probability

    FROM transactions;
    """

    cursor.execute(query)

    row = cursor.fetchone()

    cursor.close()

    connection.close()

    total = row[0]

    fraud = row[1]

    normal = row[2]

    avg_probability = row[3]

    calculated_fraud_rate = (
        (fraud / total) * 100
        if total > 0
        else 0
    )


    # --------------------------------------------------
    # Update Prometheus Metrics
    # --------------------------------------------------

    total_transactions_metric.set(total)

    fraud_transactions_metric.set(fraud)

    normal_transactions_metric.set(normal)

    fraud_rate_metric.set(calculated_fraud_rate)


    # --------------------------------------------------
    # API Response
    # --------------------------------------------------

    return {

        "total_transactions": total,

        "fraudulent_transactions": fraud,

        "normal_transactions": normal,

        "fraud_rate_percentage": round(
            calculated_fraud_rate,
            2
        ),

        "average_fraud_probability": round(
            float(avg_probability),
            4
        ),
    }


# --------------------------------------------------
# Risk Summary
# --------------------------------------------------

@app.get("/risk-summary")
def risk_summary():

    connection = get_db_connection()

    cursor = connection.cursor()

    query = """
    SELECT
        risk_level,
        COUNT(*) AS transaction_count
    FROM transactions
    GROUP BY risk_level
    ORDER BY transaction_count DESC;
    """

    cursor.execute(query)

    rows = cursor.fetchall()

    cursor.close()

    connection.close()

    result = {}

    for row in rows:

        result[row[0]] = row[1]


    # --------------------------------------------------
    # Get Risk Counts
    # --------------------------------------------------

    low_risk = result.get("LOW", 0)

    medium_risk = result.get("MEDIUM", 0)

    high_risk = result.get("HIGH", 0)


    # --------------------------------------------------
    # Update Prometheus Risk Metrics
    # --------------------------------------------------

    low_risk_transactions_metric.set(low_risk)

    medium_risk_transactions_metric.set(medium_risk)

    high_risk_transactions_metric.set(high_risk)


    # --------------------------------------------------
    # API Response
    # --------------------------------------------------

    return result


# --------------------------------------------------
# Recent Fraudulent Transactions
# --------------------------------------------------

@app.get("/recent-fraud")
def recent_fraud(limit: int = 10):

    connection = get_db_connection()

    cursor = connection.cursor()

    query = """
    SELECT
        transaction_id,
        customer_id,
        amount,
        location,
        merchant,
        fraud_probability,
        risk_level,
        transaction_timestamp
    FROM transactions
    WHERE fraud_prediction = 1
    ORDER BY id DESC
    LIMIT %s;
    """

    cursor.execute(
        query,
        (limit,)
    )

    rows = cursor.fetchall()

    cursor.close()

    connection.close()

    fraud_transactions = []

    for row in rows:

        fraud_transactions.append({

            "transaction_id": row[0],

            "customer_id": row[1],

            "amount": float(row[2]),

            "location": row[3],

            "merchant": row[4],

            "fraud_probability": float(row[5]),

            "risk_level": row[6],

            "timestamp": str(row[7]),
        })

    return {

        "count": len(fraud_transactions),

        "transactions": fraud_transactions,
    }