from functools import lru_cache
import redis.asyncio as redis

from app.config import Settings

@lru_cache(maxsize=1)
def get_redis_client() -> redis.Redis:
    settings = Settings()
    return redis.from_url(settings.redis_url, decode_responses=True)
