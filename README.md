# StreamPulse — Real-Time Fraud Detection & Analytics Platform

StreamPulse is a real-time fraud detection and analytics platform that processes financial transactions as they are generated, detects potentially fraudulent transactions using Machine Learning, stores the results in PostgreSQL and Redis, exposes REST APIs through FastAPI, and provides real-time monitoring using Prometheus and Grafana.

---

## 🚀 Project Overview

Traditional fraud detection systems often process transactions in batches.

StreamPulse demonstrates a real-time approach:

```text
Transaction Generator
        ↓
      Apache Kafka
        ↓
Spark Structured Streaming
        ↓
 Feature Engineering
        ↓
 Machine Learning Model
        ↓
 ┌───────────────┬──────────────┐
 ↓               ↓              ↓
PostgreSQL      Redis         FastAPI
                                  ↓
                             Streamlit
                              Dashboard

Monitoring:

FastAPI
   ↓
Prometheus
   ↓
Grafana