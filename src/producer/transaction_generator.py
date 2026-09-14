import random
import uuid
from datetime import datetime, timezone


LOCATIONS = [
    "Chennai",
    "Bangalore",
    "Mumbai",
    "Delhi",
    "Hyderabad",
    "Pune",
]

MERCHANTS = [
    "Amazon",
    "Flipkart",
    "Swiggy",
    "Zomato",
    "Myntra",
    "BookMyShow",
]

PAYMENT_METHODS = [
    "UPI",
    "Credit Card",
    "Debit Card",
    "Net Banking",
]

DEVICES = [
    "Mobile",
    "Laptop",
    "Tablet",
]


def generate_transaction():
    """
    Generate a synthetic transaction for StreamPulse.

    Around 10% of transactions are marked as fraud.
    Fraudulent transactions are intentionally given
    suspicious characteristics so the ML model can learn
    meaningful patterns from the synthetic data.
    """

    is_fraud = random.random() < 0.10

    if is_fraud:
        amount = round(random.uniform(50000, 150000), 2)

        device = random.choices(
            ["Unknown", "Mobile", "Laptop", "Tablet"],
            weights=[80, 7, 7, 6]
        )[0]

        location = random.choices(
            LOCATIONS + ["International", "Unknown"],
            weights=[3, 3, 3, 3, 3, 3, 35, 30]
        )[0]

        payment_method = random.choices(
            PAYMENT_METHODS,
            weights=[50, 30, 10, 10]
        )[0]

    else:
        amount = round(random.uniform(100, 10000), 2)

        device = random.choice(DEVICES)

        location = random.choice(LOCATIONS)

        payment_method = random.choice(PAYMENT_METHODS)

    transaction = {
        "transaction_id": str(uuid.uuid4()),
        "customer_id": f"C{random.randint(1001, 1005)}",
        "amount": amount,
        "location": location,
        "merchant": random.choice(MERCHANTS),
        "payment_method": payment_method,
        "device": device,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "is_fraud": is_fraud,
    }

    return transaction


if __name__ == "__main__":

    print("Testing transaction generator...\n")

    for _ in range(5):
        print(generate_transaction())