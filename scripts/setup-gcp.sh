#!/bin/bash
# Setup script for Google Cloud Platform deployment
# Run this once to set up the GCP project

set -e

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-genesis-protocol}"
REGION="${GCP_REGION:-us-central1}"
REPO_NAME="genesis"

echo "Setting up GCP project: $PROJECT_ID in region: $REGION"

# Set the project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  redis.googleapis.com \
  cloudbuild.googleapis.com \
  compute.googleapis.com

# Create Artifact Registry repository
echo "Creating Artifact Registry repository..."
gcloud artifacts repositories create $REPO_NAME \
  --repository-format=docker \
  --location=$REGION \
  --description="Genesis Protocol Docker images" \
  2>/dev/null || echo "Repository already exists"

# Create secrets (placeholders - update with real values)
echo "Creating secrets..."
echo -n "bolt://your-neo4j-host:7687" | gcloud secrets create neo4j-uri --data-file=- 2>/dev/null || echo "Secret neo4j-uri exists"
echo -n "neo4j" | gcloud secrets create neo4j-user --data-file=- 2>/dev/null || echo "Secret neo4j-user exists"
echo -n "your-neo4j-password" | gcloud secrets create neo4j-password --data-file=- 2>/dev/null || echo "Secret neo4j-password exists"
echo -n "$(openssl rand -hex 32)" | gcloud secrets create jwt-secret --data-file=- 2>/dev/null || echo "Secret jwt-secret exists"
echo -n "redis://your-redis-host:6379" | gcloud secrets create redis-url --data-file=- 2>/dev/null || echo "Secret redis-url exists"

# Create Redis instance (Memorystore)
echo "Creating Redis instance..."
gcloud redis instances create genesis-redis \
  --size=1 \
  --region=$REGION \
  --redis-version=redis_7_0 \
  --tier=basic \
  2>/dev/null || echo "Redis instance already exists or is being created"

# Create Cloud Storage bucket for content
echo "Creating Cloud Storage bucket..."
gsutil mb -l $REGION gs://${PROJECT_ID}-content 2>/dev/null || echo "Bucket already exists"

# Create service account for GitHub Actions
echo "Creating service account for CI/CD..."
SA_NAME="github-actions"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud iam service-accounts create $SA_NAME \
  --display-name="GitHub Actions" \
  2>/dev/null || echo "Service account already exists"

# Grant permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser"

# Create key for GitHub Actions
echo "Creating service account key..."
gcloud iam service-accounts keys create gcp-sa-key.json \
  --iam-account=$SA_EMAIL

echo ""
echo "=========================================="
echo "GCP Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Set up Neo4j AuraDB at https://neo4j.com/cloud/aura/"
echo "2. Update secrets with real values:"
echo "   gcloud secrets versions add neo4j-uri --data-file=-"
echo "   gcloud secrets versions add neo4j-password --data-file=-"
echo ""
echo "3. Add these GitHub Secrets:"
echo "   - GCP_PROJECT_ID: $PROJECT_ID"
echo "   - GCP_SA_KEY: (contents of gcp-sa-key.json)"
echo ""
echo "4. Get Redis URL:"
echo "   gcloud redis instances describe genesis-redis --region=$REGION"
echo ""
echo "5. Push to main branch to trigger deployment"
