#!/bin/bash
set -e

# Bootstrap script for Google Identity Platform (Root Project)
# This script sets up OAuth credentials ONCE in the root project
# All environments will use these shared credentials

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ROOT_PROJECT_ID="${1:-web-app-demo-root}"

echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Identity Platform Bootstrap (Root Project)               ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo
echo "Root Project: $ROOT_PROJECT_ID"
echo "This will create OAuth credentials that are shared across ALL environments"
echo

# Set the project
gcloud config set project "$ROOT_PROJECT_ID"

# Step 1: Enable required APIs
echo -e "${YELLOW}Step 1: Enabling required APIs in root project...${NC}"
gcloud services enable \
    identitytoolkit.googleapis.com \
    secretmanager.googleapis.com \
    iap.googleapis.com \
    --project="$ROOT_PROJECT_ID"

echo -e "${GREEN}✓ APIs enabled${NC}"
echo

# Step 2: Check if OAuth brand exists, create if not
echo -e "${YELLOW}Step 2: Setting up OAuth consent screen...${NC}"

BRAND_NAME=$(gcloud alpha iap oauth-brands list \
    --project="$ROOT_PROJECT_ID" \
    --format="value(name)" 2>/dev/null | head -1 || echo "")

if [ -z "$BRAND_NAME" ]; then
    echo "Creating OAuth brand (consent screen)..."
    echo "Note: For production, configure additional settings in GCP Console:"
    echo "      - Privacy policy URL"
    echo "      - Terms of service URL"
    echo "      - Authorized domains"
    
    # Create brand with minimal configuration
    BRAND_NAME=$(gcloud alpha iap oauth-brands create \
        --application_title="Web App Demo" \
        --support_email="$(gcloud config get-value account)" \
        --project="$ROOT_PROJECT_ID" \
        --format="value(name)")
    
    echo -e "${GREEN}✓ OAuth brand created: $BRAND_NAME${NC}"
else
    echo -e "${GREEN}✓ OAuth brand already exists: $BRAND_NAME${NC}"
fi
echo

# Step 3: Create OAuth client for Identity Platform
echo -e "${YELLOW}Step 3: Creating OAuth client credentials...${NC}"

# Check if client already exists
CLIENT_NAME="identity-platform-shared"
EXISTING_CLIENT=$(gcloud alpha iap oauth-clients list "$BRAND_NAME" \
    --project="$ROOT_PROJECT_ID" \
    --format="value(name)" \
    --filter="displayName:$CLIENT_NAME" 2>/dev/null | head -1 || echo "")

if [ -z "$EXISTING_CLIENT" ]; then
    echo "Creating new OAuth client (shared across all environments)..."
    
    CLIENT_INFO=$(gcloud alpha iap oauth-clients create "$BRAND_NAME" \
        --display_name="$CLIENT_NAME" \
        --project="$ROOT_PROJECT_ID" \
        --format="json")
    
    CLIENT_ID=$(echo "$CLIENT_INFO" | jq -r '.name' | sed 's|.*/||')
    CLIENT_SECRET=$(echo "$CLIENT_INFO" | jq -r '.secret')
    
    echo -e "${GREEN}✓ OAuth client created${NC}"
    echo "  Client ID: $CLIENT_ID"
else
    echo "OAuth client already exists..."
    CLIENT_ID=$(echo "$EXISTING_CLIENT" | sed 's|.*/||')
    
    # Note: Cannot retrieve existing secret
    echo -e "${YELLOW}⚠ Existing client found.${NC}"
    echo -e "${YELLOW}  Client ID: $CLIENT_ID${NC}"
    echo
    echo "Choose an option:"
    echo "  1. Enter the existing client secret (if you have it)"
    echo "  2. Create a new OAuth client"
    read -p "Option [1/2]: " OPTION
    
    if [ "$OPTION" = "1" ]; then
        read -sp "Enter the client secret: " CLIENT_SECRET
        echo
        if [ -z "$CLIENT_SECRET" ]; then
            echo -e "${RED}Error: Client secret cannot be empty${NC}"
            exit 1
        fi
    else
        echo "Creating new OAuth client..."
        CLIENT_NAME="identity-platform-shared-$(date +%s)"
        CLIENT_INFO=$(gcloud alpha iap oauth-clients create "$BRAND_NAME" \
            --display_name="$CLIENT_NAME" \
            --project="$ROOT_PROJECT_ID" \
            --format="json")
        
        CLIENT_ID=$(echo "$CLIENT_INFO" | jq -r '.name' | sed 's|.*/||')
        CLIENT_SECRET=$(echo "$CLIENT_INFO" | jq -r '.secret')
        echo -e "${GREEN}✓ New OAuth client created${NC}"
        echo "  Client ID: $CLIENT_ID"
    fi
fi
echo

# Step 4: Store OAuth credentials in Secret Manager (root project)
echo -e "${YELLOW}Step 4: Storing OAuth credentials in Secret Manager (root project)...${NC}"

# Create or update client_id secret
if gcloud secrets describe google_oauth_client_id --project="$ROOT_PROJECT_ID" &>/dev/null; then
    echo "Updating google_oauth_client_id secret..."
    echo -n "$CLIENT_ID" | gcloud secrets versions add google_oauth_client_id \
        --data-file=- \
        --project="$ROOT_PROJECT_ID"
else
    echo "Creating google_oauth_client_id secret..."
    echo -n "$CLIENT_ID" | gcloud secrets create google_oauth_client_id \
        --data-file=- \
        --replication-policy="automatic" \
        --project="$ROOT_PROJECT_ID"
fi

# Create or update client_secret secret
if gcloud secrets describe google_oauth_client_secret --project="$ROOT_PROJECT_ID" &>/dev/null; then
    echo "Updating google_oauth_client_secret secret..."
    echo -n "$CLIENT_SECRET" | gcloud secrets versions add google_oauth_client_secret \
        --data-file=- \
        --project="$ROOT_PROJECT_ID"
else
    echo "Creating google_oauth_client_secret secret..."
    echo -n "$CLIENT_SECRET" | gcloud secrets create google_oauth_client_secret \
        --data-file=- \
        --replication-policy="automatic" \
        --project="$ROOT_PROJECT_ID"
fi

echo -e "${GREEN}✓ OAuth credentials stored in Secret Manager${NC}"
echo

# Step 5: Create placeholder for API key
echo -e "${YELLOW}Step 5: Creating Identity Platform API key placeholder...${NC}"

if ! gcloud secrets describe identity_platform_api_key --project="$ROOT_PROJECT_ID" &>/dev/null; then
    echo "Creating identity_platform_api_key secret placeholder..."
    echo -n "PLACEHOLDER" | gcloud secrets create identity_platform_api_key \
        --data-file=- \
        --replication-policy="automatic" \
        --project="$ROOT_PROJECT_ID"
    echo -e "${YELLOW}⚠ API key secret created as placeholder${NC}"
    echo -e "${YELLOW}  Run post-terraform script after any environment configures Identity Platform${NC}"
else
    echo -e "${GREEN}✓ identity_platform_api_key secret already exists${NC}"
fi
echo

# Step 6: Create root terraform.tfvars
echo -e "${YELLOW}Step 6: Creating root Terraform variables file...${NC}"

ROOT_TFVARS_FILE="infrastructure/root/terraform.tfvars"

cat > "$ROOT_TFVARS_FILE" << EOF
# Auto-generated by bootstrap-identity-platform.sh
# Generated at: $(date -u +"%Y-%m-%d %H:%M:%S UTC")

# Root project configuration
gcp_provider_project_id = "$ROOT_PROJECT_ID"

# OAuth Credentials (shared across ALL environments)
google_oauth_client_id     = "$CLIENT_ID"
google_oauth_client_secret = "$CLIENT_SECRET"
EOF

echo -e "${GREEN}✓ Created $ROOT_TFVARS_FILE${NC}"
echo

# Summary
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Bootstrap Complete!                                       ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo
echo "OAuth credentials are now stored in the ROOT project and will be"
echo "shared across ALL environments (dev, staging, prod, etc.)"
echo
echo "Next steps:"
echo "  1. Apply root Terraform configuration:"
echo "     cd infrastructure/root"
echo "     terraform init"
echo "     terraform apply"
echo
echo "  2. Apply environment Terraform configurations (repeat for each env):"
echo "     cd infrastructure/env"
echo "     terraform init"
echo "     terraform apply -var-file=../config/dev/terraform.tfvars"
echo
echo "  3. After ANY environment is configured, run:"
echo "     ./infrastructure/scripts/post-terraform-identity-platform.sh"
echo
echo "OAuth Credentials Summary:"
echo "  Stored in: $ROOT_PROJECT_ID (root project)"
echo "  Client ID: $CLIENT_ID"
echo "  Client Secret: [stored in Secret Manager]"
echo
echo "Secret Manager secrets created in root:"
echo "  - google_oauth_client_id"
echo "  - google_oauth_client_secret"
echo "  - identity_platform_api_key (placeholder)"
echo
echo "All environments will read these secrets automatically."
echo
