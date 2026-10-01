import redis
from app.core.config import settings
import json
import logging

logger = logging.getLogger(__name__)

try:
    redis_client = redis.from_url(settings.REDIS_URL)
    redis_client.ping()
    logger.info("Redis connected")
except Exception as e:
    logger.error(f"Redis connection failed: {e}")
    redis_client = None

def cache_get(key: str):
    """Get value from cache"""
    if not redis_client:
        return None
    try:
        value = redis_client.get(key)
        return json.loads(value) if value else None
    except Exception as e:
        logger.error(f"Cache get failed: {e}")
        return None

def cache_set(key: str, value: dict, expire: int = 3600):
    """Set value in cache"""
    if not redis_client:
        return False
    try:
        redis_client.setex(key, expire, json.dumps(value))
        return True
    except Exception as e:
        logger.error(f"Cache set failed: {e}")
        return False

def cache_delete(key: str):
    """Delete value from cache"""
    if not redis_client:
        return False
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        logger.error(f"Cache delete failed: {e}")
        return False
