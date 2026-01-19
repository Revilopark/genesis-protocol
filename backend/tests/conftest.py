"""Pytest configuration and fixtures."""

import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from genesis.config import Settings, get_settings
from genesis.main import app


def get_test_settings() -> Settings:
    """Get test settings."""
    return Settings(
        environment="test",
        debug=True,
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="testpassword",
        redis_url="redis://localhost:6379",
        jwt_secret_key="test-secret-key-for-testing-only",
        clever_client_id="test_clever_id",
        clever_client_secret="test_clever_secret",
        clever_redirect_uri="http://localhost:8000/api/v1/auth/clever/callback",
        idme_client_id="test_idme_id",
        idme_client_secret="test_idme_secret",
        idme_redirect_uri="http://localhost:3000/onboarding/verify/callback",
        gcp_project_id="test-project",
        s3_content_bucket="test-bucket",
    )


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings() -> Settings:
    """Provide test settings."""
    return get_test_settings()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create sync test client."""
    # Override settings
    app.dependency_overrides[get_settings] = get_test_settings
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create async test client."""
    app.dependency_overrides[get_settings] = get_test_settings
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """Create mock authentication headers."""
    from genesis.core.security import create_access_token

    token = create_access_token(
        data={"sub": "test_user_123", "user_type": "student"},
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def guardian_auth_headers() -> dict[str, str]:
    """Create mock guardian authentication headers."""
    from genesis.core.security import create_access_token

    token = create_access_token(
        data={"sub": "test_guardian_123", "user_type": "guardian"},
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers() -> dict[str, str]:
    """Create mock admin authentication headers."""
    from genesis.core.security import create_access_token

    token = create_access_token(
        data={"sub": "test_admin_123", "user_type": "admin"},
    )
    return {"Authorization": f"Bearer {token}"}
