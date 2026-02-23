#!/bin/bash
set -e

# Post-Terraform script for Google Identity Platform
# Retrieves the Identity Platform API key and stores it in the root project
# Run this AFTER any environment has configured Identity Platform

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENV_PROJECT_ID="${1}"
ROOT_PROJECT_ID="${2:-web-app-demo-root}"

if [ -z "$ENV_PROJECT_ID" ]; then
    echo -e "${RED}Error: Environment project ID is required${NC}"
    echo "Usage: $0 <env-project-id> [root-project-id]"
    echo "Example: $0 web-app-demo-dev web-app-demo-root"
    echo
    echo "The API key will be retrieved from the environment project"
    echo "and stored in the root project's Secret Manager."
    exit 1
fi

echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Retrieving Identity Platform API Key                     ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo
echo "Environment Project: $ENV_PROJECT_ID"
echo "Root Project: $ROOT_PROJECT_ID"
echo

# Set the project to the environment where Identity Platform was configured
gcloud config set project "$ENV_PROJECT_ID"

# Retrieve Identity Platform API keys
echo -e "${YELLOW}Fetching Identity Platform API keys from $ENV_PROJECT_ID...${NC}"

# Try to get the API key using identitytoolkit API
API_KEY=$(gcloud alpha identity api-keys list \
    --project="$ENV_PROJECT_ID" \
    --filter="displayName:Browser key (auto created by Identity Platform)" \
    --format="value(keyString)" 2>/dev/null | head -1 || echo "")

if [ -z "$API_KEY" ]; then
    # Fallback: try to get any API key that might be for Identity Platform
    echo -e "${YELLOW}Trying alternative method...${NC}"
    API_KEY=$(gcloud alpha services api-keys list \
        --project="$ENV_PROJECT_ID" \
        --filter="displayName~'Identity Platform' OR displayName~'Browser key'" \
        --format="value(keyString)" 2>/dev/null | head -1 || echo "")
fi

if [ -z "$API_KEY" ]; then
    echo -e "${RED}✗ Could not automatically retrieve API key${NC}"
    echo
    echo "Please retrieve the API key manually:"
    echo "  1. Go to https://console.cloud.google.com/apis/credentials?project=$ENV_PROJECT_ID"
    echo "  2. Find the 'Browser key (auto created by Identity Platform)' or similar"
    echo "  3. Copy the API key"
    echo
    read -p "Enter the Identity Platform API key: " API_KEY
    
    if [ -z "$API_KEY" ]; then
        echo -e "${RED}Error: API key is required${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✓ API key retrieved${NC}"
echo

# Store API key in ROOT project Secret Manager
echo -e "${YELLOW}Storing API key in Secret Manager (root project: $ROOT_PROJECT_ID)...${NC}"

# Switch to root project
gcloud config set project "$ROOT_PROJECT_ID"

if gcloud secrets describe identity_platform_api_key --project="$ROOT_PROJECT_ID" &>/dev/null; then
    echo "Updating identity_platform_api_key secret..."
    echo -n "$API_KEY" | gcloud secrets versions add identity_platform_api_key \
        --data-file=- \
        --project="$ROOT_PROJECT_ID"
else
    echo "Creating identity_platform_api_key secret..."
    echo -n "$API_KEY" | gcloud secrets create identity_platform_api_key \
        --data-file=- \
        --replication-policy="automatic" \
        --project="$ROOT_PROJECT_ID"
fi

echo -e "${GREEN}✓ API key stored in root project Secret Manager${NC}"
echo

# Summary
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Setup Complete!                                           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo
echo "Identity Platform API key has been stored in the root project."
echo "All environments can now access it during deployments via:"
echo "  - Project: $ROOT_PROJECT_ID"
echo "  - Secret: identity_platform_api_key"
echo
echo "Your CI/CD pipeline will automatically inject this key during builds."
echo
