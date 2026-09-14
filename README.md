StreamPulse - Real-Time Fraud Detection & Analytics Platform
StreamPulse is a real-time fraud detection and analytics platform that processes financial transactions as they are generated, detects potentially fraudulent transactions using Machine Learning, stores results in PostgreSQL and Redis, exposes REST APIs through FastAPI, provides a Streamlit analytics dashboard, and monitors the application with Prometheus and Grafana.

Architecture


End-to-End Flow
Transaction Generator
        |
        v
   Apache Kafka
        |
        v
Spark Structured Streaming
        |
        v
 Feature Engineering
        |
        v
 Machine Learning
        |
   +----+----+
   |         |
   v         v
PostgreSQL  Redis
   |         |
   +----+----+
        |
        v
     FastAPI
        |
   +----+----+
   |         |
   v         v
Streamlit  Prometheus
Dashboard      |
               v
            Grafana
Key Features
Real-time transaction generation

Apache Kafka event streaming

Spark Structured Streaming

Machine Learning based fraud detection

Feature engineering for fraud prediction

PostgreSQL persistent storage

Redis caching

FastAPI REST API

Streamlit analytics dashboard

Docker and Docker Compose

GitHub Actions CI/CD

Prometheus metrics collection

Grafana monitoring dashboard

API health monitoring

CPU and memory monitoring

Fraud and transaction metrics

Risk-level monitoring

Automated testing with Pytest

Machine Learning
The fraud detection model is trained using synthetic transaction data.

Features
Transaction amount

Unknown device indicator

Online payment indicator

Unusual location indicator

Model
A Random Forest Classifier is used for fraud prediction.

The model produces:

Fraud prediction

Fraud probability

Risk level

The trained model is stored at:

models/fraud_model.pkl
Real-Time Streaming
Apache Kafka is used as the event streaming layer.

Transactions are continuously generated and published to the:

transactions
Kafka topic.

Spark Structured Streaming consumes these events, processes the transaction data, performs feature engineering, and sends the processed results to the storage layer.

PostgreSQL
PostgreSQL is used as the persistent database.

The transactions table stores:

Transaction ID

Customer ID

Amount

Location

Merchant

Payment method

Device

Transaction timestamp

Fraud prediction

Fraud probability

Risk score

Risk level

Redis
Redis is used as a fast caching layer.

StreamPulse caches individual transactions and recent transactions in Redis for fast access.

FastAPI
FastAPI provides the REST API layer.

Method	Endpoint	Purpose
GET	/health	Check API, model and Redis health
POST	/predict	Predict fraud for a transaction
GET	/transactions	Retrieve recent transactions
GET	/fraud-summary	Get overall fraud statistics
GET	/risk-summary	Get LOW/MEDIUM/HIGH risk distribution
GET	/recent-fraud	Retrieve recent fraudulent transactions
GET	/metrics	Prometheus metrics
Swagger API documentation:

http://localhost:8000/docs
Streamlit Dashboard
The Streamlit dashboard provides real-time fraud analytics including:

Total transactions

Fraud detected

Normal transactions

Fraud rate

Risk distribution

Recent transactions

Recent fraudulent transactions

API health status

Dashboard:

http://localhost:8501
Monitoring
StreamPulse uses Prometheus and Grafana for application and business monitoring.

Prometheus
Prometheus collects:

API request count

API response latency

API CPU usage

API memory usage

Total transactions

Fraud transactions

Normal transactions

Fraud rate

LOW-risk transactions

MEDIUM-risk transactions

HIGH-risk transactions

Configuration:

monitoring/prometheus.yml
Prometheus:

http://localhost:9090
Grafana
Grafana visualizes:

API requests

API response time

API CPU usage

API memory usage

Total transactions

Fraud transactions

Normal transactions

Fraud rate

Risk distribution

Fraud transactions over time

Fraud rate over time

Grafana:

http://localhost:3000
Docker
The project is containerized using Docker and Docker Compose.

Main services:

Kafka
PostgreSQL
Redis
Spark
FastAPI
Prometheus
Grafana
Start the services:

docker compose up -d
Check the containers:

docker compose ps
CI/CD
GitHub Actions is used for continuous integration.

The CI pipeline:

Checks out the repository

Sets up Python 3.11

Installs dependencies

Trains the ML model

Runs the automated test suite

Testing
Pytest is used for automated testing.

Tests cover:

Transaction generation

ML model functionality

FastAPI endpoints

Run tests:

pytest -v
Current test suite:

13 passed
Project Structure
StreamPulse/
|
+-- .github/
|   +-- workflows/
|
+-- src/
|   +-- producer/
|   |   +-- transaction_generator.py
|   |   +-- kafka_producer.py
|   |
|   +-- streaming/
|   |   +-- spark_stream.py
|   |   +-- postgres_writer.py
|   |   +-- ml_client.py
|   |
|   +-- fraud_detection/
|   |   +-- train_model.py
|   |   +-- predict.py
|   |
|   +-- api/
|   |   +-- fraud_api.py
|   |
|   +-- database/
|   |   +-- database.py
|   |   +-- init_db.py
|   |   +-- writer.py
|   |   +-- redis_client.py
|   |
|   +-- dashboard/
|       +-- dashboard.py
|
+-- models/
|   +-- fraud_model.pkl
|
+-- monitoring/
|   +-- prometheus.yml
|
+-- tests/
|   +-- test_generator.py
|   +-- test_model.py
|   +-- test_api.py
|
+-- data/
|   +-- raw/
|   +-- processed/
|   +-- checkpoints/
|
+-- docs/
|   +-- architecture.png
|
+-- Dockerfile
+-- Dockerfile.spark
+-- docker-compose.yml
+-- requirements.txt
+-- requirements-api.txt
+-- requirements-spark.txt
+-- .dockerignore
+-- .gitignore
+-- pytest.ini
+-- README.md
Requirements
Python 3.11+

Java 17+

Docker Desktop

Git

Running the Project
1. Clone the repository
git clone https://github.com/Suriya1903/StreamPulse.git
cd StreamPulse
2. Start Docker services
docker compose up -d
3. Start the transaction producer
From the project root:

python -m src.producer.kafka_producer
Transactions will continuously be generated and published to Kafka.

4. Access the services
Service	URL
FastAPI	http://localhost:8000
Swagger	http://localhost:8000/docs
Streamlit	http://localhost:8501
Prometheus	http://localhost:9090
Grafana	http://localhost:3000
Example Fraud Prediction
Example request:

{
  "amount": 75000,
  "unknown_device": 1,
  "online_payment": 1,
  "unusual_location": 1
}
Example response:

{
  "fraud_prediction": 1,
  "fraud_probability": 1.0,
  "risk_level": "HIGH"
}
Technology Stack
Programming
Python

Streaming and Data Processing
Apache Kafka

Apache Spark Structured Streaming

Pandas

NumPy

Machine Learning
Scikit-learn

Random Forest

Joblib

Backend
FastAPI

Uvicorn

Databases
PostgreSQL

Redis

Visualization
Streamlit

Grafana

Monitoring
Prometheus

Prometheus FastAPI Instrumentator

DevOps
Docker

Docker Compose

Git

GitHub Actions

Testing
Pytest

HTTPX

Project Goals
StreamPulse demonstrates an end-to-end production-style data and ML pipeline involving:

Real-time event streaming

Stream processing

Machine Learning inference

Persistent and cached storage

REST API development

Interactive analytics

Containerization

CI/CD

Application monitoring

Author
Suriya MG

GitHub: https://github.com/Suriya1903/StreamPulse
