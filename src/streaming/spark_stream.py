from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DoubleType,
    BooleanType,
)

from pyspark.sql.functions import (
    from_json,
    col,
    when,
)

from postgres_writer import save_batch


# --------------------------------------------------
# Create Spark session
# --------------------------------------------------

spark = (
    SparkSession.builder
    .appName("StreamPulse-FraudDetection")
    .master("local[*]")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")


# --------------------------------------------------
# Kafka transaction schema
# --------------------------------------------------

transaction_schema = StructType([

    StructField(
        "transaction_id",
        StringType(),
        True
    ),

    StructField(
        "customer_id",
        StringType(),
        True
    ),

    StructField(
        "amount",
        DoubleType(),
        True
    ),

    StructField(
        "location",
        StringType(),
        True
    ),

    StructField(
        "merchant",
        StringType(),
        True
    ),

    StructField(
        "payment_method",
        StringType(),
        True
    ),

    StructField(
        "device",
        StringType(),
        True
    ),

    StructField(
        "timestamp",
        StringType(),
        True
    ),

    StructField(
        "is_fraud",
        BooleanType(),
        True
    ),
])


# --------------------------------------------------
# Read from Kafka
# --------------------------------------------------

kafka_df = (
    spark.readStream
    .format("kafka")
    .option(
        "kafka.bootstrap.servers",
        "localhost:9092"
    )
    .option(
        "subscribe",
        "transactions"
    )
    .option(
        "startingOffsets",
        "latest"
    )
    .option(
        "failOnDataLoss",
        "true"
    )
    .load()
)


# --------------------------------------------------
# Convert Kafka JSON
# --------------------------------------------------

json_df = kafka_df.select(
    from_json(
        col("value").cast("string"),
        transaction_schema
    ).alias("data")
)


transactions = json_df.select("data.*")


# --------------------------------------------------
# Feature engineering
# --------------------------------------------------

transactions = (
    transactions

    .withColumn(
        "high_amount",
        when(
            col("amount") >= 50000,
            1
        ).otherwise(0)
    )

    .withColumn(
        "unknown_device",
        when(
            col("device") == "Unknown",
            1
        ).otherwise(0)
    )

    .withColumn(
        "online_payment",
        when(
            col("payment_method").isin(
                "UPI",
                "Credit Card",
                "Debit Card",
                "Net Banking"
            ),
            1
        ).otherwise(0)
    )

    .withColumn(
        "unusual_location",
        when(
            col("location").isin(
                "Unknown",
                "International"
            ),
            1
        ).otherwise(0)
    )
)


# --------------------------------------------------
# Calculate risk score
# --------------------------------------------------

transactions = transactions.withColumn(
    "risk_score",

    col("high_amount")
    + col("unknown_device")
    + col("online_payment")
    + col("unusual_location")
)


# --------------------------------------------------
# Initial rule-based risk level
# --------------------------------------------------

transactions = transactions.withColumn(
    "rule_risk_level",

    when(
        col("risk_score") >= 3,
        "HIGH"
    )

    .when(
        col("risk_score") == 2,
        "MEDIUM"
    )

    .otherwise("LOW")
)


# --------------------------------------------------
# Select required columns
# --------------------------------------------------

result = transactions.select(

    "transaction_id",
    "customer_id",
    "amount",
    "location",
    "merchant",
    "payment_method",
    "device",
    "timestamp",

    "high_amount",
    "unknown_device",
    "online_payment",
    "unusual_location",

    "risk_score"
)


# --------------------------------------------------
# Start streaming query
# --------------------------------------------------

query = (
    result.writeStream

    .outputMode("append")

    .foreachBatch(save_batch)

    # NEW checkpoint name
    # This avoids the old corrupted checkpoint.
    .option(
        "checkpointLocation",
        "data/checkpoints/fraud_detection_v2"
    )

    .start()
)


print("\n======================================")
print("StreamPulse Spark Streaming Started")
print("======================================")
print("Kafka      : localhost:9092")
print("Topic      : transactions")
print("PostgreSQL : localhost:5433")
print("Checkpoint : fraud_detection_v2")
print("\nWaiting for transactions...\n")


query.awaitTermination()