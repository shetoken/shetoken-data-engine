#!/bin/bash
# Deploy SHEtoken API to Google Cloud Run
# Run: chmod +x deploy_api.sh && ./deploy_api.sh

source ../.env 2>/dev/null || true
PROJECT_ID="${GCP_PROJECT_ID:?Set GCP_PROJECT_ID in .env}"
REGION="${GCP_REGION:-us-central1}"
SERVICE="shetoken-api"
IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/shetoken/$SERVICE:latest"

echo "Deploying SHEtoken API to Cloud Run..."

# Build
gcloud builds submit --tag=$IMAGE --project=$PROJECT_ID .

# Deploy
gcloud run deploy $SERVICE \
  --image=$IMAGE \
  --region=$REGION \
  --project=$PROJECT_ID \
  --allow-unauthenticated \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=10 \
  --port=8080

echo ""
echo "API deployed!"
echo "URL: $(gcloud run services describe $SERVICE --region=$REGION --format='value(status.url)')"
echo "Docs: $(gcloud run services describe $SERVICE --region=$REGION --format='value(status.url)')/docs"
