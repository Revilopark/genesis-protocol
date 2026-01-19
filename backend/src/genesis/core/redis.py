"""Redis client for caching and pub/sub."""

import logging
from typing import AsyncGenerator

import redis.asyncio as redis

from genesis.config import settings

logger = logging.getLogger(__name__)

_redis_client: redis.Redis | None = None  # type: ignore[type-arg]
_redis_available: bool = False


async def init_redis() -> None:
    """Initialize Redis connection."""
    global _redis_client, _redis_available
    try:
        _redis_client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
        )
        # Verify connectivity
        await _redis_client.ping()
        _redis_available = True
        logger.info("Redis connection established successfully")
    except Exception as e:
        logger.warning(f"Failed to connect to Redis: {e}. Caching will be unavailable.")
        _redis_available = False
        if _redis_client:
            await _redis_client.aclose()
            _redis_client = None


async def close_redis() -> None:
    """Close Redis connection."""
    global _redis_client
    if _redis_client:
        await _redis_client.aclose()
        _redis_client = None


def get_redis() -> redis.Redis:  # type: ignore[type-arg]
    """Get the Redis client instance."""
    if _redis_client is None:
        raise RuntimeError("Redis client not initialized")
    return _redis_client


async def get_redis_client() -> AsyncGenerator[redis.Redis, None]:  # type: ignore[type-arg]
    """FastAPI dependency for Redis client."""
    yield get_redis()
