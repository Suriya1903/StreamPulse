import json
import time

from kafka import KafkaProducer

from transaction_generator import generate_transaction


producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda value: json.dumps(value).encode("utf-8")
)


print("StreamPulse Kafka Producer Started...")


try:

    while True:

        transaction = generate_transaction()

        producer.send(
            "transactions",
            value=transaction
        )

        print(f"Sent transaction: {transaction}")

        time.sleep(2)


except KeyboardInterrupt:

    print("\nProducer stopped.")

finally:

    producer.close()