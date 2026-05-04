#!/bin/bash
# SHEtoken Agent — Google Cloud Deployment Script
# Run this once to deploy. Weekly runs happen automatically after.
#
# Prerequisites:
#   1. Install Google Cloud SDK: cloud.google.com/sdk
#   2. Run: gcloud auth login
#   3. Fill in GCP_PROJECT_ID in .env
#   4. Run: chmod +x deploy.sh && ./deploy.sh

set -e
source .env 2>/dev/null || true

PROJECT_ID="${GCP_PROJECT_ID:?Set GCP_PROJECT_ID in .env}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="wei-agent"
IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/shetoken/$SERVICE_NAME:latest"

echo "======================================"
echo "SHEtoken Agent — Cloud Run Deployment"
echo "Project: $PROJECT_ID"
echo "Region:  $REGION"
echo "======================================"

# 1. Enable required APIs
echo "[1/7] Enabling APIs..."
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    cloudscheduler.googleapis.com \
    artifactregistry.googleapis.com \
    --project=$PROJECT_ID

# 2. Create Artifact Registry repo
echo "[2/7] Creating Artifact Registry..."
gcloud artifacts repositories create shetoken \
    --repository-format=docker \
    --location=$REGION \
    --project=$PROJECT_ID 2>/dev/null || echo "  (already exists)"

# 3. Build and push Docker image
echo "[3/7] Building Docker image (this takes ~5 minutes first time)..."
gcloud builds submit \
    --tag=$IMAGE \
    --project=$PROJECT_ID \
    .

# 4. Create service account for the job
echo "[4/7] Creating service account..."
SA_NAME="shetoken-agent-sa"
SA_EMAIL="$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"
gcloud iam service-accounts create $SA_NAME \
    --display-name="SHEtoken WEI Agent" \
    --project=$PROJECT_ID 2>/dev/null || echo "  (already exists)"

# 5. Create Cloud Run Job
echo "[5/7] Creating Cloud Run Job..."
gcloud run jobs create $SERVICE_NAME \
    --image=$IMAGE \
    --region=$REGION \
    --project=$PROJECT_ID \
    --service-account=$SA_EMAIL \
    --memory=8Gi \
    --cpu=4 \
    --task-timeout=3600 \
    --set-env-vars="GMAIL_USER=${GMAIL_USER}" \
    --set-env-vars="GMAIL_APP_PASSWORD=${GMAIL_APP_PASSWORD}" \
    --set-env-vars="REPORT_TO_EMAIL=${REPORT_TO_EMAIL}" \
    --set-env-vars="GOOGLE_SHEET_ID=${GOOGLE_SHEET_ID}" \
    2>/dev/null || \
gcloud run jobs update $SERVICE_NAME \
    --image=$IMAGE \
    --region=$REGION \
    --project=$PROJECT_ID \
    --memory=8Gi \
    --cpu=4

# 6. Create Cloud Scheduler (runs every Sunday 6am UTC)
echo "[6/7] Creating weekly schedule..."
gcloud scheduler jobs create http shetoken-weekly-agent \
    --schedule="0 6 * * 0" \
    --uri="https://$REGION-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/$PROJECT_ID/jobs/$SERVICE_NAME:run" \
    --message-body="{}" \
    --oauth-service-account-email=$SA_EMAIL \
    --location=$REGION \
    --project=$PROJECT_ID \
    2>/dev/null || echo "  (scheduler already exists)"

# 7. Test run
echo "[7/7] Running test job..."
gcloud run jobs execute $SERVICE_NAME \
    --region=$REGION \
    --project=$PROJECT_ID

echo ""
echo "======================================"
echo "Deployment complete!"
echo ""
echo "Weekly schedule: Every Sunday 6:00 AM UTC"
echo "Monitor at: console.cloud.google.com/run/jobs"
echo ""
echo "To run manually:"
echo "  gcloud run jobs execute $SERVICE_NAME --region=$REGION"
echo ""
echo "To view logs:"
echo "  gcloud run jobs executions list --job=$SERVICE_NAME --region=$REGION"
echo "======================================"
