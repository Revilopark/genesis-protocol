"""Neo4j database connection management."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from neo4j import AsyncDriver, AsyncGraphDatabase, AsyncSession

from genesis.config import settings

_driver: AsyncDriver | None = None


async def init_neo4j() -> None:
    """Initialize Neo4j connection pool."""
    global _driver
    _driver = AsyncGraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
        max_connection_pool_size=settings.neo4j_max_connection_pool_size,
    )
    # Verify connectivity
    async with _driver.session(database=settings.neo4j_database) as session:
        await session.run("RETURN 1")


async def close_neo4j() -> None:
    """Close Neo4j connection pool."""
    global _driver
    if _driver:
        await _driver.close()
        _driver = None


def get_driver() -> AsyncDriver:
    """Get the Neo4j driver instance."""
    if _driver is None:
        raise RuntimeError("Neo4j driver not initialized")
    return _driver


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for getting a Neo4j session."""
    driver = get_driver()
    async with driver.session(database=settings.neo4j_database) as session:
        yield session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for Neo4j session."""
    async with get_session() as session:
        yield session
