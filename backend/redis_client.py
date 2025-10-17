"""
Redis Client Configuration
Handles Redis connection and basic operations
"""
import redis
import json
import os
from typing import Optional, Any
from datetime import timedelta


# Redis connection configuration
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "redis123")
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# Create Redis client
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    db=REDIS_DB,
    decode_responses=True,  # Automatically decode byte responses to strings
    socket_connect_timeout=5,
    socket_keepalive=True,
    health_check_interval=30
)


def check_redis_connection() -> bool:
    """
    Check if Redis connection is healthy

    Returns:
        bool: True if connected, False otherwise
    """
    try:
        redis_client.ping()
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False


def set_value(key: str, value: Any, expire: Optional[int] = None) -> bool:
    """
    Set a value in Redis with optional expiration

    Args:
        key: Redis key
        value: Value to store (will be JSON serialized if not string)
        expire: Expiration time in seconds (optional)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Serialize value if it's not a string
        if not isinstance(value, str):
            value = json.dumps(value)

        if expire:
            redis_client.setex(key, expire, value)
        else:
            redis_client.set(key, value)

        return True
    except Exception as e:
        print(f"❌ Redis set failed for key '{key}': {e}")
        return False


def get_value(key: str, deserialize: bool = True) -> Optional[Any]:
    """
    Get a value from Redis

    Args:
        key: Redis key
        deserialize: Whether to JSON deserialize the value

    Returns:
        The value or None if not found
    """
    try:
        value = redis_client.get(key)

        if value is None:
            return None

        # Try to deserialize JSON if requested
        if deserialize:
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value

        return value
    except Exception as e:
        print(f"❌ Redis get failed for key '{key}': {e}")
        return None


def delete_value(key: str) -> bool:
    """
    Delete a value from Redis

    Args:
        key: Redis key to delete

    Returns:
        bool: True if deleted, False otherwise
    """
    try:
        result = redis_client.delete(key)
        return result > 0
    except Exception as e:
        print(f"❌ Redis delete failed for key '{key}': {e}")
        return False


def exists(key: str) -> bool:
    """
    Check if a key exists in Redis

    Args:
        key: Redis key

    Returns:
        bool: True if exists, False otherwise
    """
    try:
        return redis_client.exists(key) > 0
    except Exception as e:
        print(f"❌ Redis exists check failed for key '{key}': {e}")
        return False


def get_ttl(key: str) -> int:
    """
    Get time-to-live for a key

    Args:
        key: Redis key

    Returns:
        int: TTL in seconds, -1 if no expiry, -2 if key doesn't exist
    """
    try:
        return redis_client.ttl(key)
    except Exception as e:
        print(f"❌ Redis TTL check failed for key '{key}': {e}")
        return -2


def extend_expiry(key: str, additional_seconds: int) -> bool:
    """
    Extend the expiration time of a key

    Args:
        key: Redis key
        additional_seconds: Additional seconds to add to TTL

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        current_ttl = redis_client.ttl(key)
        if current_ttl > 0:
            redis_client.expire(key, current_ttl + additional_seconds)
            return True
        return False
    except Exception as e:
        print(f"❌ Redis extend expiry failed for key '{key}': {e}")
        return False


def get_keys_by_pattern(pattern: str) -> list:
    """
    Get all keys matching a pattern

    Args:
        pattern: Redis key pattern (e.g., "session:*")

    Returns:
        list: List of matching keys
    """
    try:
        return redis_client.keys(pattern)
    except Exception as e:
        print(f"❌ Redis keys search failed for pattern '{pattern}': {e}")
        return []


def delete_by_pattern(pattern: str) -> int:
    """
    Delete all keys matching a pattern

    Args:
        pattern: Redis key pattern (e.g., "session:*")

    Returns:
        int: Number of keys deleted
    """
    try:
        keys = redis_client.keys(pattern)
        if keys:
            return redis_client.delete(*keys)
        return 0
    except Exception as e:
        print(f"❌ Redis pattern delete failed for pattern '{pattern}': {e}")
        return 0


def get_redis_info() -> dict:
    """
    Get Redis server information

    Returns:
        dict: Redis server info
    """
    try:
        info = redis_client.info()
        return {
            "connected": True,
            "version": info.get("redis_version"),
            "used_memory": info.get("used_memory_human"),
            "connected_clients": info.get("connected_clients"),
            "uptime_days": info.get("uptime_in_days")
        }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e)
        }


# Health check on module import
if __name__ == "__main__":
    if check_redis_connection():
        print("✅ Redis connection successful")
        print(f"Redis info: {get_redis_info()}")
    else:
        print("❌ Redis connection failed")
