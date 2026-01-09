import redis
import json
import os
from typing import List, Dict

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

def get_redis_client():
    """Create and return a Redis client"""
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

def save_message(session_id: str, role: str, content: str):
    """
    Save a message to Redis list for a given session.
    Format: JSON string {"role": role, "content": content}
    """
    try:
        client = get_redis_client()
        message = json.dumps({"role": role, "content": content})
        # Push to the right (end) of the list
        client.rpush(f"chat:{session_id}", message)
        # Set expiry to 30 days (optional, to prevent infinite growth)
        client.expire(f"chat:{session_id}", 30 * 24 * 60 * 60) 
    except Exception as e:
        print(f"Error saving message to Redis: {e}")

def get_history(session_id: str) -> List[Dict[str, str]]:
    """
    Retrieve full chat history for a session.
    Returns list of dicts: [{"role": "user", "content": "..."}]
    """
    try:
        client = get_redis_client()
        # Get all elements from the list
        messages = client.lrange(f"chat:{session_id}", 0, -1)
        # Parse JSON strings back to dicts
        return [json.loads(msg) for msg in messages]
    except Exception as e:
        print(f"Error retrieving history from Redis: {e}")
        return []

def clear_history(session_id: str):
    """Clear history for a session"""
    try:
        client = get_redis_client()
        client.delete(f"chat:{session_id}")
    except Exception as e:
        print(f"Error clearing history: {e}")
