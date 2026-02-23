# Infrastructure Bootstrap Guide

## Quick Setup (New Project)

Follow these steps to set up Identity Platform for **all** environments in one go:

### Step 1: Bootstrap Root Project (One-Time Only)

```bash
./infrastructure/scripts/bootstrap-identity-platform.sh web-app-demo-root
```

This creates OAuth credentials that will be shared across all environments.

**What this does**:
- ✅ Creates OAuth consent screen
- ✅ Creates OAuth client credentials
- ✅ Stores credentials in root project Secret Manager
- ✅ Generates `infrastructure/root/terraform.tfvars`

**Output**: OAuth credentials stored in `web-app-demo-root` project

### Step 2: Apply Root Terraform

```bash
cd infrastructure/root
terraform init
terraform apply
```

**What this does**:
- ✅ Creates Secret Manager resources
- ✅ Sets up IAM permissions for GitHub Actions
- ✅ Makes secrets available to all environments

### Step 3: Apply Environment Terraform

For **each** environment (dev, prod, staging, etc.):

```bash
cd infrastructure/env

# Dev environment
terraform init
terraform apply -var-file=../config/dev/terraform.tfvars

# Prod environment  
terraform apply -var-file=../config/prod/terraform.tfvars
```

**What this does**:
- ✅ Reads OAuth credentials from root project
- ✅ Configures Identity Platform with environment-specific authorized domains
- ✅ Deploys Cloud Run services

### Step 4: Store Identity Platform API Key

After **any** environment is configured, run:

```bash
./infrastructure/scripts/post-terraform-identity-platform.sh web-app-demo-dev web-app-demo-root
```

**What this does**:
- ✅ Retrieves auto-created Identity Platform API key
- ✅ Stores it in root project Secret Manager
- ✅ Makes it available to all environments

**Done!** All environments are now configured.

## Key Benefits

### Before (Per-Environment Bootstrap)
- ❌ Run bootstrap for dev
- ❌ Run bootstrap for staging
- ❌ Run bootstrap for prod
- ❌ Manage 3+ sets of OAuth credentials
- ❌ Complex terraform.tfvars with secrets

### After (Centralized Root Bootstrap)
- ✅ Run bootstrap **once** for root
- ✅ All environments use same credentials
- ✅ Simple terraform.tfvars (just project IDs)
- ✅ Single source of truth
- ✅ Much faster to add new environments

## Architecture

```
┌─────────────────────────────────────────────┐
│ Root Project (web-app-demo-root)           │
│                                             │
│ ┌─────────────────────────────────────┐   │
│ │ Secret Manager                       │   │
│ │  • google_oauth_client_id           │   │
│ │  • google_oauth_client_secret       │   │
│ │  • identity_platform_api_key        │   │
│ └─────────────────────────────────────┘   │
│                                             │
│ ┌─────────────────────────────────────┐   │
│ │ OAuth Consent Screen                 │   │
│ │ OAuth Client (shared)               │   │
│ └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
                    │
                    │ reads secrets via
                    │ data sources
                    ▼
    ┌───────────────┴───────────────┐
    │                               │
┌───▼─────────────┐     ┌───────────▼──────┐
│ Dev Environment │     │ Prod Environment │
│                 │     │                  │
│ • Identity      │     │ • Identity       │
│   Platform      │     │   Platform       │
│ • Authorized    │     │ • Authorized     │
│   domains (dev) │     │   domains (prod) │
│ • Cloud Run     │     │ • Cloud Run      │
└─────────────────┘     └──────────────────┘
```

## Adding a New Environment

To add a new environment (e.g., `staging`):

### 1. Create terraform.tfvars

```bash
cat > infrastructure/config/staging/terraform.tfvars << EOF
project_id = "web-app-demo-staging"
root_project_id = "web-app-demo-root"
EOF
```

### 2. Apply Terraform

```bash
cd infrastructure/env
terraform apply -var-file=../config/staging/terraform.tfvars
```

**That's it!** No bootstrap needed. The new environment automatically:
- Reads OAuth credentials from root
- Configures Identity Platform
- Sets up authorized domains
- Deploys services

## Configuration Files

### Root Project

**File**: `infrastructure/root/terraform.tfvars`
```hcl
gcp_provider_project_id = "web-app-demo-root"
google_oauth_client_id = "123456789-abc.apps.googleusercontent.com"
google_oauth_client_secret = "GOCSPX-xxxxxxxxxxxx"
```

⚠️ Contains secrets - do not commit!

### Environment Projects

**File**: `infrastructure/config/dev/terraform.tfvars`
```hcl
project_id = "web-app-demo-dev"
root_project_id = "web-app-demo-root"
```

✅ No secrets - safe to commit (but gitignored)

## Secrets Flow

### Infrastructure Deployment
```
GitHub Actions
    │
    ├── infrastructure-prod job
    │   └── Reads from: web-app-demo-root
    │       • google_oauth_client_id
    │       • google_oauth_client_secret
    │   └── Passes to Terraform as TF_VAR_*
    │
    └── infrastructure-dev job
        └── Reads from: web-app-demo-root
            • google_oauth_client_id
            • google_oauth_client_secret
        └── Passes to Terraform as TF_VAR_*
```

### Frontend Deployment
```
GitHub Actions
    │
    ├── frontend-prod job
    │   └── Reads from: web-app-demo-root
    │       • google_oauth_client_id
    │       • identity_platform_api_key
    │   └── Injects into .env file
    │
    └── frontend-dev job
        └── Reads from: web-app-demo-root
            • google_oauth_client_id
            • identity_platform_api_key
        └── Injects into .env file
```

## Troubleshooting

### "Permission denied" accessing secrets

**Problem**: Environment can't read secrets from root

**Solution**: Ensure GitHub Actions service account has access:
```bash
# This is automated in root Terraform, but manual fix:
gcloud secrets add-iam-policy-binding google_oauth_client_id \
  --project=web-app-demo-root \
  --member="serviceAccount:github-actions@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### "API key is PLACEHOLDER"

**Problem**: Forgot to run post-terraform script

**Solution**:
```bash
./infrastructure/scripts/post-terraform-identity-platform.sh web-app-demo-dev web-app-demo-root
```

### "OAuth brand already exists"

**Problem**: Re-running bootstrap script

**Solution**: This is normal! Script will use existing brand.

## Rotating Credentials

To rotate OAuth credentials (affects all environments):

```bash
# 1. Re-run bootstrap
./infrastructure/scripts/bootstrap-identity-platform.sh web-app-demo-root
# Choose option to create new OAuth client

# 2. Update root Terraform
cd infrastructure/root
terraform apply

# 3. All environments automatically use new credentials!
```

No need to update each environment separately.

## Summary

| Aspect | Before | After |
|--------|--------|-------|
| Bootstrap runs | Per environment (3+) | Once (root only) |
| OAuth credentials | Per environment (3+ sets) | Shared (1 set) |
| terraform.tfvars | Contains secrets | No secrets |
| New environment setup | Bootstrap + Terraform | Terraform only |
| Credential rotation | Update all environments | Update root only |
| Secret management | Distributed | Centralized |

**Result**: Simpler, faster, more maintainable infrastructure!

## Next Steps

After bootstrapping:
1. ✅ Commit your changes (tfvars are gitignored)
2. ✅ Push to GitHub to trigger CI/CD
3. ✅ Verify deployments succeed
4. ✅ Test OAuth login flow in each environment

## Support

- **Scripts**: See `infrastructure/scripts/README.md`
- **Root Terraform**: See `infrastructure/root/gcp_identity_platform.tf`
- **Env Terraform**: See `infrastructure/env/gcp_identity_platform.tf`
- **Workflows**: See `.github/workflows/push-commit.yaml`
