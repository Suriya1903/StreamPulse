import os
import random

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split


# --------------------------------------------------
# Configuration
# --------------------------------------------------

random.seed(42)

NUMBER_OF_TRANSACTIONS = 10000

FEATURES = [
    "amount",
    "unknown_device",
    "online_payment",
    "unusual_location",
]


# --------------------------------------------------
# Generate synthetic training data
# --------------------------------------------------

data = []


for _ in range(NUMBER_OF_TRANSACTIONS):

    is_fraud = random.random() < 0.10

    if is_fraud:

        amount = random.uniform(
            50000,
            150000
        )

        unknown_device = random.choices(
            [0, 1],
            weights=[20, 80]
        )[0]

        online_payment = random.choices(
            [0, 1],
            weights=[20, 80]
        )[0]

        unusual_location = random.choices(
            [0, 1],
            weights=[30, 70]
        )[0]

    else:

        amount = random.uniform(
            100,
            10000
        )

        unknown_device = random.choices(
            [0, 1],
            weights=[95, 5]
        )[0]

        online_payment = random.choices(
            [0, 1],
            weights=[60, 40]
        )[0]

        unusual_location = random.choices(
            [0, 1],
            weights=[98, 2]
        )[0]

    data.append({

        "amount": amount,

        "unknown_device":
            unknown_device,

        "online_payment":
            online_payment,

        "unusual_location":
            unusual_location,

        "is_fraud":
            int(is_fraud),
    })


# --------------------------------------------------
# Create DataFrame
# --------------------------------------------------

df = pd.DataFrame(data)

print("\nDataset created successfully.")

print("\nFirst 5 rows:")
print(df.head())

print("\nClass distribution:")
print(df["is_fraud"].value_counts())


# --------------------------------------------------
# Features and target
# --------------------------------------------------

X = df[FEATURES]

y = df["is_fraud"]


# --------------------------------------------------
# Train/test split
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,

    test_size=0.20,

    random_state=42,

    stratify=y,
)


# --------------------------------------------------
# Train Random Forest
# --------------------------------------------------

model = RandomForestClassifier(

    n_estimators=100,

    random_state=42,

    class_weight="balanced",
)


model.fit(
    X_train,
    y_train
)


# --------------------------------------------------
# Evaluate model
# --------------------------------------------------

predictions = model.predict(X_test)

probabilities = model.predict_proba(
    X_test
)[:, 1]


accuracy = accuracy_score(
    y_test,
    predictions
)


roc_auc = roc_auc_score(
    y_test,
    probabilities
)


print("\n======================================")
print("MODEL EVALUATION")
print("======================================")

print(
    f"Accuracy : {accuracy:.4f}"
)

print(
    f"ROC-AUC  : {roc_auc:.4f}"
)

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        predictions
    )
)


# --------------------------------------------------
# Save model
# --------------------------------------------------

os.makedirs(
    "models",
    exist_ok=True
)


model_bundle = {

    "model": model,

    "features": FEATURES,
}


model_path = "models/fraud_model.pkl"


joblib.dump(
    model_bundle,
    model_path
)


print(
    f"\nModel saved successfully:"
)

print(
    model_path
)