# Genesis Protocol Backend

FastAPI backend for The Genesis Protocol - Daily personalized comic book and video content generation platform.

## Features

- Multi-agent AI system ("The Rooms") for content generation
- Neo4j graph database for Canon/Variant topology
- JWT authentication with Clever SSO integration
- Redis caching for performance
- OpenTelemetry instrumentation

## Development

```bash
# Install dependencies
uv sync

# Run development server
uv run uvicorn genesis.main:app --reload

# Run tests
uv run pytest

# Run linting
uv run ruff check src/
uv run mypy src/genesis
```

## Environment Variables

- `NEO4J_URI` - Neo4j database URI
- `NEO4J_USER` - Neo4j username
- `NEO4J_PASSWORD` - Neo4j password
- `REDIS_URL` - Redis connection URL
- `JWT_SECRET_KEY` - Secret key for JWT tokens
- `ENVIRONMENT` - Environment name (development, production)
