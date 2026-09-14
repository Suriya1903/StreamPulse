from src.producer.transaction_generator import generate_transaction


def test_transaction_has_required_fields():

    transaction = generate_transaction()

    required_fields = [
        "transaction_id",
        "customer_id",
        "amount",
        "location",
        "merchant",
        "payment_method",
        "device",
        "timestamp",
        "is_fraud",
    ]

    for field in required_fields:

        assert field in transaction


def test_transaction_amount_is_positive():

    transaction = generate_transaction()

    assert transaction["amount"] > 0


def test_customer_id_format():

    transaction = generate_transaction()

    assert transaction["customer_id"].startswith("C")


def test_fraud_value_is_boolean():

    transaction = generate_transaction()

    assert isinstance(
        transaction["is_fraud"],
        bool
    )


def test_transaction_id_is_unique():

    transaction1 = generate_transaction()

    transaction2 = generate_transaction()

    assert (
        transaction1["transaction_id"]
        !=
        transaction2["transaction_id"]
    )