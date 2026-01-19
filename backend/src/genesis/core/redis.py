"""Redis client for caching and pub/sub."""

from typing import AsyncGenerator

import redis.asyncio as redis

from genesis.config import settings

_redis_client: redis.Redis | None = None  # type: ignore[type-arg]


async def init_redis() -> None:
    """Initialize Redis connection."""
    global _redis_client
    _redis_client = redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )
    # Verify connectivity
    await _redis_client.ping()


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
