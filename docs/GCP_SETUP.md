# Google Cloud Platform Setup Guide

This guide walks you through setting up GCP resources for The Genesis Protocol deployment.

## Prerequisites

- Google Cloud account with billing enabled
- `gcloud` CLI installed ([Installation Guide](https://cloud.google.com/sdk/docs/install))
- GitHub repository with Actions enabled

## 1. Create GCP Project

```bash
# Create new project
gcloud projects create genesis-protocol-prod --name="Genesis Protocol"

# Set as default project
gcloud config set project genesis-protocol-prod

# Enable billing (required for Cloud Run)
# Visit: https://console.cloud.google.com/billing/linkedaccount?project=genesis-protocol-prod
```

## 2. Enable Required APIs

```bash
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  cloudbuild.googleapis.com \
  aiplatform.googleapis.com \
  storage.googleapis.com
```

## 3. Create Artifact Registry Repository

```bash
gcloud artifacts repositories create genesis \
  --repository-format=docker \
  --location=us-central1 \
  --description="Genesis Protocol container images"
```

## 4. Create Service Account for GitHub Actions

```bash
# Create service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions Deployer"

# Get the service account email
SA_EMAIL="github-actions@genesis-protocol-prod.iam.gserviceaccount.com"

# Grant required roles
gcloud projects add-iam-policy-binding genesis-protocol-prod \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding genesis-protocol-prod \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding genesis-protocol-prod \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding genesis-protocol-prod \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/iam.serviceAccountUser"

# Create and download key
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=$SA_EMAIL

echo "Key saved to github-actions-key.json"
```

## 5. Create Secrets in Secret Manager

```bash
# Neo4j connection
echo -n "bolt://your-neo4j-host:7687" | \
  gcloud secrets create neo4j-uri --data-file=-

echo -n "neo4j" | \
  gcloud secrets create neo4j-user --data-file=-

echo -n "your-neo4j-password" | \
  gcloud secrets create neo4j-password --data-file=-

# Redis connection (use Memorystore or external provider)
echo -n "redis://your-redis-host:6379" | \
  gcloud secrets create redis-url --data-file=-

# JWT secret (generate with: openssl rand -hex 32)
echo -n "your-jwt-secret-key" | \
  gcloud secrets create jwt-secret --data-file=-

# Gemini API key (from Google AI Studio)
echo -n "your-gemini-api-key" | \
  gcloud secrets create gemini-api-key --data-file=-
```

## 6. Configure GitHub Secrets

Go to your repository: **Settings → Secrets and variables → Actions**

Add these secrets:

| Secret Name | Value |
|-------------|-------|
| `GCP_PROJECT_ID` | `genesis-protocol-prod` |
| `GCP_SA_KEY` | Contents of `github-actions-key.json` |

**Important:** Delete `github-actions-key.json` after adding to GitHub:
```bash
rm github-actions-key.json
```

## 7. Create Cloud Storage Bucket (Optional)

For storing generated comics and videos:

```bash
# Create bucket
gsutil mb -l us-central1 gs://genesis-content-prod

# Set CORS for frontend access
cat > cors.json << 'EOF'
[
  {
    "origin": ["*"],
    "method": ["GET", "HEAD"],
    "responseHeader": ["Content-Type"],
    "maxAgeSeconds": 3600
  }
]
EOF
gsutil cors set cors.json gs://genesis-content-prod
rm cors.json

# Make objects publicly readable (for CDN)
gsutil iam ch allUsers:objectViewer gs://genesis-content-prod
```

## 8. Set Up Neo4j AuraDB

1. Go to [Neo4j Aura](https://neo4j.com/cloud/aura/)
2. Create a new AuraDB instance
3. Note the connection URI, username, and password
4. Update the secrets in Secret Manager

## 9. Set Up Redis (Memorystore)

```bash
# Create Redis instance
gcloud redis instances create genesis-redis \
  --size=1 \
  --region=us-central1 \
  --redis-version=redis_7_0

# Get the IP address
gcloud redis instances describe genesis-redis --region=us-central1 \
  --format="value(host)"
```

**Note:** Memorystore requires VPC access. For Cloud Run, you'll need to configure a VPC connector.

### Alternative: Use Upstash Redis (Serverless)

1. Go to [Upstash](https://upstash.com/)
2. Create a Redis database
3. Use the REST URL for Cloud Run compatibility

## 10. Deploy Manually (First Time)

```bash
# Build and push backend
cd backend
docker build -t us-central1-docker.pkg.dev/genesis-protocol-prod/genesis/genesis-api:latest .
docker push us-central1-docker.pkg.dev/genesis-protocol-prod/genesis/genesis-api:latest

# Deploy backend
gcloud run deploy genesis-api \
  --image us-central1-docker.pkg.dev/genesis-protocol-prod/genesis/genesis-api:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8080

# Get backend URL
BACKEND_URL=$(gcloud run services describe genesis-api --region us-central1 --format='value(status.url)')

# Build and push frontend
cd ../frontend
docker build --build-arg NEXT_PUBLIC_API_URL=$BACKEND_URL \
  -t us-central1-docker.pkg.dev/genesis-protocol-prod/genesis/genesis-frontend:latest .
docker push us-central1-docker.pkg.dev/genesis-protocol-prod/genesis/genesis-frontend:latest

# Deploy frontend
gcloud run deploy genesis-frontend \
  --image us-central1-docker.pkg.dev/genesis-protocol-prod/genesis/genesis-frontend:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --port 3000
```

## 11. Verify Deployment

```bash
# Check services
gcloud run services list --region us-central1

# Get URLs
echo "Backend: $(gcloud run services describe genesis-api --region us-central1 --format='value(status.url)')"
echo "Frontend: $(gcloud run services describe genesis-frontend --region us-central1 --format='value(status.url)')"

# Test health endpoint
curl $(gcloud run services describe genesis-api --region us-central1 --format='value(status.url)')/health
```

## Cost Optimization

### Cloud Run Settings
- **Min instances:** 0 (scale to zero when idle)
- **Max instances:** 10 (adjust based on traffic)
- **CPU allocation:** Only during requests
- **Memory:** 2Gi for backend, 1Gi for frontend

### Estimated Monthly Costs (Low Traffic)
| Service | Estimated Cost |
|---------|---------------|
| Cloud Run | $0-50 (pay per use) |
| Artifact Registry | $1-5 |
| Secret Manager | $0.06/secret/month |
| Neo4j Aura | $65+ (Free tier available) |
| Memorystore/Upstash | $0-30 |
| **Total** | ~$70-150/month |

## Troubleshooting

### Check Cloud Run Logs
```bash
gcloud run services logs read genesis-api --region us-central1 --limit 50
```

### View Secret Versions
```bash
gcloud secrets versions list neo4j-uri
```

### Test Local Docker Build
```bash
docker build -t genesis-api ./backend
docker run -p 8000:8080 genesis-api
```

## Security Checklist

- [ ] Service account has minimal required permissions
- [ ] Secrets are stored in Secret Manager (not env vars)
- [ ] Cloud Run services use HTTPS only
- [ ] VPC connector configured for internal services
- [ ] Audit logging enabled
- [ ] Budget alerts configured
