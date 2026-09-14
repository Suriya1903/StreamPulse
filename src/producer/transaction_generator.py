import random
import uuid
import time
from datetime import datetime


CUSTOMERS = [
    "C1001",
    "C1002",
    "C1003",
    "C1004",
    "C1005",
]


LOCATIONS = [
    "Chennai",
    "Bangalore",
    "Mumbai",
    "Delhi",
    "Hyderabad",
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

    transaction = {
        "transaction_id": str(uuid.uuid4()),

        "customer_id": random.choice(CUSTOMERS),

        "amount": round(random.uniform(100, 100000), 2),

        "location": random.choice(LOCATIONS),

        "merchant": random.choice(MERCHANTS),

        "payment_method": random.choice(PAYMENT_METHODS),

        "device": random.choice(DEVICES),

        "timestamp": datetime.now().isoformat()
    }

    return transaction


if __name__ == "__main__":

    print("Starting StreamPulse Transaction Generator...\n")

    while True:

        transaction = generate_transaction()

        print(transaction)

        time.sleep(2)

def generate_transaction():

    customer_id = random.choice(CUSTOMERS)

    is_fraud = random.random() < 0.10

    if is_fraud:

        amount = round(random.uniform(50000, 150000), 2)
        location = random.choice(LOCATIONS)
        device = "Unknown"

    else:

        amount = round(random.uniform(100, 10000), 2)
        location = random.choice(LOCATIONS)
        device = random.choice(DEVICES)

    transaction = {
        "transaction_id": str(uuid.uuid4()),
        "customer_id": customer_id,
        "amount": amount,
        "location": location,
        "merchant": random.choice(MERCHANTS),
        "payment_method": random.choice(PAYMENT_METHODS),
        "device": device,
        "timestamp": datetime.now().isoformat(),
        "is_fraud": is_fraud
    }

    return transaction