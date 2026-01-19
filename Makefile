.PHONY: help install dev test lint format docker-up docker-down clean

help:
	@echo "Genesis Protocol - Development Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  install       Install all dependencies"
	@echo "  dev           Start local development environment"
	@echo "  test          Run all tests"
	@echo "  lint          Run linters"
	@echo "  format        Format code"
	@echo "  docker-up     Start Docker services"
	@echo "  docker-down   Stop Docker services"
	@echo "  clean         Clean build artifacts"

install:
	cd backend && uv sync
	cd frontend && npm ci

dev: docker-up
	@echo "Starting development servers..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo "Neo4j Browser: http://localhost:7474"

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

test:
	cd backend && uv run pytest tests/ -v --cov=genesis
	cd frontend && npm run test

test-backend:
	cd backend && uv run pytest tests/ -v --cov=genesis

test-frontend:
	cd frontend && npm run test

lint:
	cd backend && uv run ruff check src/
	cd backend && uv run mypy src/genesis
	cd frontend && npm run lint

format:
	cd backend && uv run ruff format src/
	cd frontend && npm run format

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .next -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/.venv frontend/node_modules

seed-db:
	cd backend && uv run python -m genesis.scripts.seed_neo4j

migrate-db:
	cd backend && uv run python -m genesis.scripts.migrate_neo4j
