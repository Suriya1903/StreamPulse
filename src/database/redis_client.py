import json

import redis


# --------------------------------------------------
# Redis configuration
# --------------------------------------------------

REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379


redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
)


# --------------------------------------------------
# Test connection
# --------------------------------------------------

def check_redis_connection():

    return redis_client.ping()


# --------------------------------------------------
# Store transaction
# --------------------------------------------------

def cache_transaction(transaction):

    key = f"transaction:{transaction['transaction_id']}"

    redis_client.set(
        key,
        json.dumps(transaction),
        ex=3600,
    )


# --------------------------------------------------
# Get transaction
# --------------------------------------------------

def get_cached_transaction(transaction_id):

    key = f"transaction:{transaction_id}"

    data = redis_client.get(key)

    if data is None:
        return None

    return json.loads(data)


# --------------------------------------------------
# Store recent transactions
# --------------------------------------------------

def add_recent_transaction(transaction):

    redis_client.lpush(
        "recent_transactions",
        json.dumps(transaction),
    )

    # Keep only latest 100 transactions
    redis_client.ltrim(
        "recent_transactions",
        0,
        99,
    )


# --------------------------------------------------
# Get recent transactions
# --------------------------------------------------

def get_recent_transactions(limit=20):

    data = redis_client.lrange(
        "recent_transactions",
        0,
        limit - 1,
    )

    return [
        json.loads(item)
        for item in data
    ]