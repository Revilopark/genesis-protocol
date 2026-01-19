"""Application configuration management."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    debug: bool = False
    environment: str = Field(default="development", description="development, staging, production")

    # Neo4j
    neo4j_uri: str = Field(default="bolt://localhost:7687")
    neo4j_user: str = Field(default="neo4j")
    neo4j_password: str = Field(default="")
    neo4j_database: str = Field(default="neo4j")
    neo4j_max_connection_pool_size: int = Field(default=50)

    # Redis
    redis_url: str = Field(default="redis://localhost:6379")

    # JWT
    jwt_secret_key: str = Field(default="")
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_expire_minutes: int = Field(default=30)

    # Clever SSO
    clever_client_id: str = Field(default="")
    clever_client_secret: str = Field(default="")
    clever_redirect_uri: str = Field(default="")

    # ID.me
    idme_client_id: str = Field(default="")
    idme_client_secret: str = Field(default="")
    idme_redirect_uri: str = Field(default="")

    # Google Cloud / Vertex AI
    gcp_project_id: str = Field(default="")
    gcp_location: str = Field(default="us-central1")
    vertex_ai_endpoint: str | None = Field(default=None)

    # Google AI Studio (Gemini API)
    gemini_api_key: str = Field(default="")

    # AWS
    aws_region: str = Field(default="us-east-1")
    s3_content_bucket: str = Field(default="")

    # Cloudflare
    cloudflare_api_token: str | None = Field(default=None)
    cloudflare_zone_id: str | None = Field(default=None)

    # CORS - use "*" to allow all origins in production
    # Cloud Run URLs are dynamic, so we allow all origins
    cors_origins: list[str] = Field(default=["*"])

    # Rate Limiting
    rate_limit_requests_per_minute: int = Field(default=60)


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


settings = get_settings()
