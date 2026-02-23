#!/bin/bash
set -e

# Bootstrap script for Google Identity Platform
# This script automates the setup of OAuth credentials and Identity Platform
# Run this BEFORE applying Terraform configuration for a new environment

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

echo -e "${GREEN}Starting Identity Platform bootstrap for project: $PROJECT_ID${NC}"
echo "Environment: $ENVIRONMENT"
echo

# Set the project
gcloud config set project "$PROJECT_ID"

# Step 1: Enable required APIs
echo -e "${YELLOW}Step 1: Enabling required APIs...${NC}"
gcloud services enable \
    identitytoolkit.googleapis.com \
    secretmanager.googleapis.com \
    iap.googleapis.com \
    --project="$PROJECT_ID"

echo -e "${GREEN}✓ APIs enabled${NC}"
echo

# Step 2: Check if OAuth brand exists, create if not
echo -e "${YELLOW}Step 2: Setting up OAuth consent screen...${NC}"

BRAND_NAME=$(gcloud alpha iap oauth-brands list \
    --project="$PROJECT_ID" \
    --format="value(name)" 2>/dev/null | head -1 || echo "")

if [ -z "$BRAND_NAME" ]; then
    echo "Creating OAuth brand (consent screen)..."
    echo "Note: You may need to configure additional settings in the GCP Console"
    echo "      for production applications (privacy policy, terms of service, etc.)"
    
    # Create brand with minimal configuration
    BRAND_NAME=$(gcloud alpha iap oauth-brands create \
        --application_title="Web App Demo - $ENVIRONMENT" \
        --support_email="$(gcloud config get-value account)" \
        --project="$PROJECT_ID" \
        --format="value(name)")
    
    echo -e "${GREEN}✓ OAuth brand created: $BRAND_NAME${NC}"
else
    echo -e "${GREEN}✓ OAuth brand already exists: $BRAND_NAME${NC}"
fi
echo

# Step 3: Create OAuth client for Identity Platform
echo -e "${YELLOW}Step 3: Creating OAuth client credentials...${NC}"

# Check if client already exists for this environment
CLIENT_NAME="identity-platform-$ENVIRONMENT"
EXISTING_CLIENT=$(gcloud alpha iap oauth-clients list "$BRAND_NAME" \
    --project="$PROJECT_ID" \
    --format="value(name)" \
    --filter="displayName:$CLIENT_NAME" 2>/dev/null | head -1 || echo "")

if [ -z "$EXISTING_CLIENT" ]; then
    echo "Creating new OAuth client..."
    
    CLIENT_INFO=$(gcloud alpha iap oauth-clients create "$BRAND_NAME" \
        --display_name="$CLIENT_NAME" \
        --project="$PROJECT_ID" \
        --format="json")
    
    CLIENT_ID=$(echo "$CLIENT_INFO" | jq -r '.name' | sed 's|.*/||')
    CLIENT_SECRET=$(echo "$CLIENT_INFO" | jq -r '.secret')
    
    echo -e "${GREEN}✓ OAuth client created${NC}"
    echo "  Client ID: $CLIENT_ID"
else
    echo "OAuth client already exists, retrieving credentials..."
    CLIENT_ID=$(echo "$EXISTING_CLIENT" | sed 's|.*/||')
    
    # Note: Cannot retrieve existing secret, user must provide it or create new client
    echo -e "${YELLOW}⚠ Existing client found. If you don't have the secret, create a new client.${NC}"
    echo -e "${YELLOW}  Client ID: $CLIENT_ID${NC}"
    echo
    read -p "Enter the client secret (or press Enter to create a new client): " CLIENT_SECRET
    
    if [ -z "$CLIENT_SECRET" ]; then
        echo "Creating new OAuth client..."
        CLIENT_NAME="identity-platform-$ENVIRONMENT-$(date +%s)"
        CLIENT_INFO=$(gcloud alpha iap oauth-clients create "$BRAND_NAME" \
            --display_name="$CLIENT_NAME" \
            --project="$PROJECT_ID" \
            --format="json")
        
        CLIENT_ID=$(echo "$CLIENT_INFO" | jq -r '.name' | sed 's|.*/||')
        CLIENT_SECRET=$(echo "$CLIENT_INFO" | jq -r '.secret')
        echo -e "${GREEN}✓ New OAuth client created${NC}"
        echo "  Client ID: $CLIENT_ID"
    fi
fi
echo

# Step 4: Store OAuth credentials in Secret Manager
echo -e "${YELLOW}Step 4: Storing OAuth credentials in Secret Manager...${NC}"

# Create or update client_id secret
if gcloud secrets describe google_oauth_client_id --project="$PROJECT_ID" &>/dev/null; then
    echo "Updating google_oauth_client_id secret..."
    echo -n "$CLIENT_ID" | gcloud secrets versions add google_oauth_client_id \
        --data-file=- \
        --project="$PROJECT_ID"
else
    echo "Creating google_oauth_client_id secret..."
    echo -n "$CLIENT_ID" | gcloud secrets create google_oauth_client_id \
        --data-file=- \
        --replication-policy="automatic" \
        --project="$PROJECT_ID"
fi

# Create or update client_secret secret
if gcloud secrets describe google_oauth_client_secret --project="$PROJECT_ID" &>/dev/null; then
    echo "Updating google_oauth_client_secret secret..."
    echo -n "$CLIENT_SECRET" | gcloud secrets versions add google_oauth_client_secret \
        --data-file=- \
        --project="$PROJECT_ID"
else
    echo "Creating google_oauth_client_secret secret..."
    echo -n "$CLIENT_SECRET" | gcloud secrets create google_oauth_client_secret \
        --data-file=- \
        --replication-policy="automatic" \
        --project="$PROJECT_ID"
fi

echo -e "${GREEN}✓ OAuth credentials stored in Secret Manager${NC}"
echo

# Step 5: Initialize Identity Platform and retrieve API key
echo -e "${YELLOW}Step 5: Retrieving Identity Platform API key...${NC}"
echo "Note: The API key is created automatically when Identity Platform is configured."
echo "      This will be retrieved after Terraform creates the Identity Platform config."
echo

# Create placeholder for API key secret (will be populated after Terraform runs)
if ! gcloud secrets describe identity_platform_api_key --project="$PROJECT_ID" &>/dev/null; then
    echo "Creating identity_platform_api_key secret placeholder..."
    echo -n "PLACEHOLDER_RUN_TERRAFORM_FIRST" | gcloud secrets create identity_platform_api_key \
        --data-file=- \
        --replication-policy="automatic" \
        --project="$PROJECT_ID"
    echo -e "${YELLOW}⚠ API key secret created as placeholder${NC}"
    echo -e "${YELLOW}  Run the post-terraform script after applying Terraform to populate it${NC}"
else
    echo -e "${GREEN}✓ identity_platform_api_key secret already exists${NC}"
fi
echo

# Step 6: Create tfvars file with credentials
echo -e "${YELLOW}Step 6: Creating Terraform variables file...${NC}"

TFVARS_FILE="infrastructure/config/$ENVIRONMENT/terraform.tfvars"
mkdir -p "infrastructure/config/$ENVIRONMENT"

cat > "$TFVARS_FILE" << EOF
# Auto-generated by bootstrap-identity-platform.sh
# Generated at: $(date -u +"%Y-%m-%d %H:%M:%S UTC")

# Project Configuration
project_id = "$PROJECT_ID"

# OAuth Credentials (injected from Secret Manager during CI/CD)
# These values are also stored in Secret Manager for GitHub Actions
google_oauth_client_id     = "$CLIENT_ID"
google_oauth_client_secret = "$CLIENT_SECRET"
EOF

echo -e "${GREEN}✓ Created $TFVARS_FILE${NC}"
echo

# Summary
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Bootstrap Complete!                                       ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo
echo "Next steps:"
echo "  1. Review and update $TFVARS_FILE if needed"
echo "  2. Run Terraform to create Identity Platform:"
echo "     cd infrastructure/env"
echo "     terraform init"
echo "     terraform apply -var-file=../config/$ENVIRONMENT/terraform.tfvars"
echo
echo "  3. After Terraform completes, run the post-terraform script:"
echo "     ./infrastructure/scripts/post-terraform-identity-platform.sh $PROJECT_ID $ENVIRONMENT"
echo
echo "OAuth Credentials Summary:"
echo "  Client ID: $CLIENT_ID"
echo "  Client Secret: [stored in Secret Manager]"
echo "  Secret Manager secrets created:"
echo "    - google_oauth_client_id"
echo "    - google_oauth_client_secret"
echo "    - identity_platform_api_key (placeholder)"
echo
