#!/bin/bash
set -e

# Post-Terraform script for Google Identity Platform
# This script retrieves the Identity Platform API key after Terraform has created the config
# Run this AFTER applying Terraform configuration

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${1}"
ENVIRONMENT="${2:-dev}"

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: PROJECT_ID is required${NC}"
    echo "Usage: $0 <project-id> [environment]"
    echo "Example: $0 web-app-demo-dev dev"
    exit 1
fi

echo -e "${GREEN}Retrieving Identity Platform API key for project: $PROJECT_ID${NC}"
echo "Environment: $ENVIRONMENT"
echo

# Set the project
gcloud config set project "$PROJECT_ID"

# Retrieve Identity Platform API keys
echo -e "${YELLOW}Fetching Identity Platform API keys...${NC}"

# Try to get the API key using identitytoolkit API
API_KEY=$(gcloud alpha identity api-keys list \
    --project="$PROJECT_ID" \
    --filter="displayName:Browser key (auto created by Identity Platform)" \
    --format="value(keyString)" 2>/dev/null | head -1 || echo "")

if [ -z "$API_KEY" ]; then
    # Fallback: try to get any API key that might be for Identity Platform
    echo -e "${YELLOW}Trying alternative method to retrieve API key...${NC}"
    API_KEY=$(gcloud alpha services api-keys list \
        --project="$PROJECT_ID" \
        --filter="displayName~'Identity Platform' OR displayName~'Browser key'" \
        --format="value(keyString)" 2>/dev/null | head -1 || echo "")
fi

if [ -z "$API_KEY" ]; then
    echo -e "${RED}✗ Could not automatically retrieve API key${NC}"
    echo
    echo "Please retrieve the API key manually:"
    echo "  1. Go to https://console.cloud.google.com/apis/credentials?project=$PROJECT_ID"
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

# Store API key in Secret Manager
echo -e "${YELLOW}Storing API key in Secret Manager...${NC}"

if gcloud secrets describe identity_platform_api_key --project="$PROJECT_ID" &>/dev/null; then
    echo "Updating identity_platform_api_key secret..."
    echo -n "$API_KEY" | gcloud secrets versions add identity_platform_api_key \
        --data-file=- \
        --project="$PROJECT_ID"
else
    echo "Creating identity_platform_api_key secret..."
    echo -n "$API_KEY" | gcloud secrets create identity_platform_api_key \
        --data-file=- \
        --replication-policy="automatic" \
        --project="$PROJECT_ID"
fi

echo -e "${GREEN}✓ API key stored in Secret Manager${NC}"
echo

# Summary
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Post-Terraform Setup Complete!                           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo
echo "Identity Platform API key has been stored in Secret Manager."
echo "Your CI/CD pipeline can now access it during deployments."
echo
echo "Next steps:"
echo "  - Deploy your frontend and backend services"
echo "  - The API key will be automatically injected during build"
echo
