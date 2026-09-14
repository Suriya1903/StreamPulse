import json
import time

from kafka import KafkaProducer

from src.producer.transaction_generator import generate_transaction


KAFKA_SERVER = "localhost:9092"
TOPIC = "transactions"


producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda value: json.dumps(value).encode("utf-8")
)


print("===================================")
print("StreamPulse Kafka Producer Started")
print("===================================")
print(f"Kafka Server : {KAFKA_SERVER}")
print(f"Topic        : {TOPIC}")
print("Sending one transaction every 2 seconds...")
print("Press Ctrl+C to stop.\n")


try:

    while True:

        transaction = generate_transaction()

        producer.send(
            TOPIC,
            value=transaction
        )

        producer.flush()

        print(
            f"Sent | "
            f"ID: {transaction['transaction_id'][:8]} | "
            f"Amount: ₹{transaction['amount']:.2f} | "
            f"Location: {transaction['location']} | "
            f"Device: {transaction['device']} | "
            f"Fraud: {transaction['is_fraud']}"
        )

        time.sleep(2)


except KeyboardInterrupt:

    print("\nProducer stopped by user.")


finally:

    producer.close()
    print("Kafka producer closed.")