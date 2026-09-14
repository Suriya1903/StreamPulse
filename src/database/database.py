import psycopg2


DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 5433,
    "database": "streampulse",
    "user": "streampulse",
    "password": "streampulse_password",
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)