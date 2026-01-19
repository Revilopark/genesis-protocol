# The Genesis Protocol

Daily personalized comic book and video content generation platform within a centralized fictional universe.

## Architecture Overview

- **Backend**: FastAPI (Python) - Modular monolith architecture
- **Database**: Neo4j AuraDB - Hierarchical graph for Canon/Variant topology
- **Frontend**: Next.js + React + Tailwind CSS (Guardian Dashboard)
- **Orchestration**: Amazon EKS (Kubernetes)
- **AI/ML**: Google Gemini 1.5 Pro, Veo 3.1, Imagen 3
- **CI/CD**: GitHub Actions → ArgoCD

## Project Structure

```
genesis-protocol/
├── .github/workflows/     # CI/CD pipelines
├── backend/               # FastAPI modular monolith
├── frontend/              # Next.js Guardian Dashboard
├── infra/
│   ├── terraform/         # Infrastructure as Code
│   └── kubernetes/        # K8s manifests (Kustomize)
├── argocd/                # ArgoCD application definitions
├── scripts/               # Development utilities
└── docs/                  # Documentation
```

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- Docker & Docker Compose
- uv (Python package manager)

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/genesis-protocol.git
   cd genesis-protocol
   ```

2. Copy environment variables:
   ```bash
   cp .env.example .env
   ```

3. Start local services:
   ```bash
   docker-compose up -d
   ```

4. Install backend dependencies:
   ```bash
   cd backend
   uv sync
   ```

5. Run the backend:
   ```bash
   uv run uvicorn genesis.main:app --reload
   ```

6. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

7. Run the frontend:
   ```bash
   npm run dev
   ```

## API Documentation

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Testing

### Backend
```bash
cd backend
uv run pytest tests/ -v
```

### Frontend
```bash
cd frontend
npm run test
```

## Deployment

Deployments are managed via GitOps with ArgoCD:

1. Push changes to `main` branch
2. CI pipeline builds and pushes Docker images to ECR
3. Image tags are updated in `infra/kubernetes/overlays/`
4. ArgoCD syncs changes to the cluster

## Key Modules

### Backend Modules

- **auth**: Clever SSO + ID.me authentication
- **heroes**: User hero management (Variant layer)
- **social**: Friend connections and presence
- **canon**: Global universe state
- **content**: Episode generation orchestration
- **rooms**: AI agents (Writers Room, Art Department, Studio)
- **guardian**: Parent dashboard backend
- **moderation**: Content safety pipeline

### Content Pipeline

1. **Writers Room** (Gemini 1.5 Pro): Script generation
2. **Art Department** (Imagen 3): Panel generation with Character Locker
3. **Studio** (Veo 3.1 + Parallax): Video synthesis

## License

Proprietary - All rights reserved
