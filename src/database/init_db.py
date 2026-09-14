from src.database.database import get_connection


CREATE_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,

    transaction_id VARCHAR(100) UNIQUE NOT NULL,

    customer_id VARCHAR(100),

    amount NUMERIC(12, 2),

    location VARCHAR(100),

    merchant VARCHAR(100),

    payment_method VARCHAR(50),

    device VARCHAR(100),

    transaction_timestamp TIMESTAMP,

    fraud_prediction INTEGER,

    fraud_probability NUMERIC(6, 4),

    risk_score INTEGER,

    risk_level VARCHAR(20),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


def initialize_database():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(CREATE_TABLE_QUERY)

    connection.commit()

    cursor.close()
    connection.close()

    print("Transactions table created successfully.")


if __name__ == "__main__":
    initialize_database()