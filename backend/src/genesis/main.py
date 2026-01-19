"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from genesis.config import settings
from genesis.core.database import close_neo4j, init_neo4j, _connection_available as neo4j_available
from genesis.core.middleware import RequestLoggingMiddleware
from genesis.core.redis import close_redis, init_redis, _redis_available as redis_available

# Import routers
from genesis.auth.router import router as auth_router
from genesis.canon.router import router as canon_router
from genesis.content.router import router as content_router
from genesis.guardian.router import router as guardian_router
from genesis.heroes.router import router as heroes_router
from genesis.jobs.router import router as jobs_router
from genesis.moderation.router import router as moderation_router
from genesis.social.router import router as social_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifecycle manager."""
    # Startup
    print("Starting database connections...", flush=True)
    await init_neo4j()
    await init_redis()
    print(f"Database connections initialized. Neo4j: {neo4j_available}, Redis: {redis_available}", flush=True)
    yield
    # Shutdown
    await close_neo4j()
    await close_redis()


def create_app() -> FastAPI:
    """Application factory pattern."""
    app = FastAPI(
        title="The Genesis Protocol API",
        description="Daily personalized comic book and video content generation",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/api/docs" if settings.debug else None,
        redoc_url="/api/redoc" if settings.debug else None,
    )

    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)

    # Mount routers with prefixes
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(heroes_router, prefix="/api/v1/heroes", tags=["Heroes"])
    app.include_router(social_router, prefix="/api/v1/social", tags=["Social"])
    app.include_router(canon_router, prefix="/api/v1/canon", tags=["Canon"])
    app.include_router(content_router, prefix="/api/v1/content", tags=["Content"])
    app.include_router(guardian_router, prefix="/api/v1/guardian", tags=["Guardian"])
    app.include_router(moderation_router, prefix="/api/v1/moderation", tags=["Moderation"])
    app.include_router(jobs_router, prefix="/api/v1/jobs", tags=["Jobs"])

    # Health check
    @app.get("/health")
    async def health_check() -> dict[str, str]:
        return {"status": "healthy", "version": app.version or "1.0.0"}

    # Readiness check
    @app.get("/ready")
    async def readiness_check() -> dict[str, str]:
        # Could add database connectivity checks here
        return {"status": "ready"}

    # Debug endpoint for connection status
    @app.get("/debug/connections")
    async def connection_status() -> dict[str, bool | str]:
        from genesis.core.database import _connection_available as neo4j_conn
        from genesis.core.redis import _redis_available as redis_conn
        return {
            "neo4j_connected": neo4j_conn,
            "redis_connected": redis_conn,
            "neo4j_uri": settings.neo4j_uri[:30] + "..." if len(settings.neo4j_uri) > 30 else settings.neo4j_uri,
            "gemini_api_key_set": bool(settings.gemini_api_key),
            "gemini_api_key_prefix": settings.gemini_api_key[:10] + "..." if settings.gemini_api_key else "NOT SET",
            "gcp_project_id": settings.gcp_project_id or "NOT SET",
        }

    return app


app = create_app()
