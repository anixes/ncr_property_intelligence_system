#!/bin/bash
# ─────────────────────────────────────────────────────────────
# NCR Property Price Estimator — EC2 Deployment Script
# ─────────────────────────────────────────────────────────────
# Prerequisites:
#   sudo apt-get update && sudo apt-get install -y docker.io
#   sudo systemctl enable docker && sudo systemctl start docker
#   sudo usermod -aG docker ubuntu && newgrp docker
#
# Login to GHCR (once):
#   echo <YOUR_PAT> | docker login ghcr.io -u anixes --password-stdin
# ─────────────────────────────────────────────────────────────

set -e

API_IMAGE="ghcr.io/anixes/ncr-property-api:v1"
FRONTEND_IMAGE="ghcr.io/anixes/ncr-property-frontend:v1"
NETWORK="ncr-net"

echo ">>> Pulling latest images..."
docker pull "$API_IMAGE"
docker pull "$FRONTEND_IMAGE"

echo ">>> Stopping old containers (if any)..."
docker stop ncr-frontend ncr-api 2>/dev/null || true
docker rm   ncr-frontend ncr-api 2>/dev/null || true

echo ">>> Creating Docker network '${NETWORK}'..."
docker network create "$NETWORK" 2>/dev/null || true

echo ">>> Starting API container..."
docker run -d \
  --name ncr-api \
  --network "$NETWORK" \
  -p 8000:8000 \
  --restart unless-stopped \
  "$API_IMAGE"

echo ">>> Waiting for API health check..."
sleep 10

echo ">>> Starting Frontend container..."
docker run -d \
  --name ncr-frontend \
  --network "$NETWORK" \
  -p 8501:8501 \
  -e API_BASE_URL=http://ncr-api:8000 \
  --restart unless-stopped \
  "$FRONTEND_IMAGE"

echo ">>> Deployment complete. Container status:"
docker ps --filter "name=ncr-"
echo ""
echo "  API:      http://<EC2_PUBLIC_IP>:8000/docs"
echo "  Frontend: http://<EC2_PUBLIC_IP>:8501"
