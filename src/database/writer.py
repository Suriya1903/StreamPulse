from database import get_connection


def save_transaction(transaction):

    connection = get_connection()

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
        risk_level
    )
    VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s
    )
    ON CONFLICT (transaction_id)
    DO NOTHING;
    """

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
            transaction["timestamp"],
            transaction["fraud_prediction"],
            transaction["fraud_probability"],
            transaction["risk_level"]
        )
    )

    connection.commit()

    cursor.close()
    connection.close()