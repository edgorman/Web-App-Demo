# Infrastructure Bootstrap Scripts

This directory contains scripts to automate the setup of Google Identity Platform and OAuth credentials in the root project.

## Overview

Identity Platform and OAuth credentials are configured **ONCE** in the root project and shared across **ALL** environments (dev, staging, prod, etc.). This eliminates the need to bootstrap each environment separately.

## Quick Start

### One-Time Root Setup

Run this **once** to set up Identity Platform for all environments:

```bash
# 1. Bootstrap Identity Platform in root project
./infrastructure/scripts/bootstrap-identity-platform.sh web-app-demo-root

# 2. Apply root Terraform
cd infrastructure/root
terraform init
terraform apply

# 3. Apply environment Terraform (for each environment)
cd infrastructure/env
terraform apply -var-file=../config/dev/terraform.tfvars
terraform apply -var-file=../config/prod/terraform.tfvars

# 4. Retrieve and store API key (after ANY environment is configured)
cd ../..
./infrastructure/scripts/post-terraform-identity-platform.sh web-app-demo-dev web-app-demo-root
```

That's it! All environments now share the same OAuth credentials.

## Why This Approach?

### Centralized Management
- ✅ OAuth credentials created **once** in root project
- ✅ All environments use the **same** credentials
- ✅ No per-environment OAuth client management
- ✅ Simpler secret rotation (update root, all envs inherit)

### Simplified Bootstrapping
- ✅ Bootstrap script run **once** instead of per-environment
- ✅ Fewer manual steps
- ✅ Less room for error
- ✅ Faster environment setup

### Security
- ✅ All secrets centralized in root project
- ✅ Environment projects read secrets via data sources
- ✅ IAM controls access to secrets
- ✅ Audit logs in single location

## Script Details

### 1. bootstrap-identity-platform.sh

**Purpose**: One-time setup of OAuth credentials in root project

**Usage**:
```bash
./bootstrap-identity-platform.sh [root-project-id]
```

**Default**: `web-app-demo-root`

**What it does**:
- Enables required APIs in root project
- Creates OAuth consent screen (brand)
- Creates OAuth client credentials (shared)
- Stores credentials in root project Secret Manager
- Creates `infrastructure/root/terraform.tfvars`

**Output**:
- Secrets in root project:
  - `google_oauth_client_id`
  - `google_oauth_client_secret`
  - `identity_platform_api_key` (placeholder)
- File: `infrastructure/root/terraform.tfvars`

### 2. post-terraform-identity-platform.sh

**Purpose**: Retrieve Identity Platform API key after environment is configured

**Usage**:
```bash
./post-terraform-identity-platform.sh <env-project-id> [root-project-id]
```

**Example**:
```bash
./post-terraform-identity-platform.sh web-app-demo-dev web-app-demo-root
```

**What it does**:
- Retrieves API key from environment project (where Identity Platform was configured)
- Stores API key in root project Secret Manager
- Makes API key available to all environments

**Note**: Run this after **any** environment has configured Identity Platform. You only need to run it once, not per environment.

## Architecture

```
Root Project (web-app-demo-root)
├── OAuth Client Credentials (shared)
│   ├── google_oauth_client_id
│   └── google_oauth_client_secret
├── Identity Platform API Key (shared)
│   └── identity_platform_api_key
└── GitHub Actions Service Account

Environment Projects
├── Dev (web-app-demo-dev)
│   ├── Identity Platform Config
│   │   ├── Reads OAuth creds from root
│   │   └── Authorized domains: localhost + dev URLs
│   └── Cloud Run Services (backend, frontend)
│
└── Prod (web-app-demo-prod)
    ├── Identity Platform Config
    │   ├── Reads OAuth creds from root
    │   └── Authorized domains: localhost + prod URLs
    └── Cloud Run Services (backend, frontend)
```

## Environment Configuration

Each environment's `terraform.tfvars` is minimal:

```hcl
# infrastructure/config/dev/terraform.tfvars
project_id = "web-app-demo-dev"
root_project_id = "web-app-demo-root"
```

No OAuth credentials needed! They're read from root automatically.

## Terraform Data Sources

Environments read secrets using data sources:

```hcl
# infrastructure/env/gcp_identity_platform.tf
data "google_secret_manager_secret_version" "google_oauth_client_id" {
  project = var.root_project_id  # web-app-demo-root
  secret  = "google_oauth_client_id"
}

resource "google_identity_platform_default_supported_idp_config" "google" {
  client_id = data.google_secret_manager_secret_version.google_oauth_client_id.secret_data
  # ...
}
```

## CI/CD Integration

GitHub Actions read secrets from root project:

```yaml
- id: secrets
  uses: ./.github/actions/gcp-secret-manager
  with:
    project_id: 'web-app-demo-root'  # Always root!
    secrets_list: |
      GOOGLE_OAUTH_CLIENT_ID=google_oauth_client_id
      IDENTITY_PLATFORM_API_KEY=identity_platform_api_key
```

All environments get the same secrets automatically.

## Adding a New Environment

To add a new environment (e.g., staging):

1. **No bootstrap needed!** OAuth credentials already exist in root.

2. Create config file:
```bash
cat > infrastructure/config/staging/terraform.tfvars << EOF
project_id = "web-app-demo-staging"
root_project_id = "web-app-demo-root"
EOF
```

3. Apply Terraform:
```bash
cd infrastructure/env
terraform apply -var-file=../config/staging/terraform.tfvars
```

That's it! The new environment uses existing OAuth credentials from root.

## Rotating Credentials

To rotate OAuth credentials (affects **all** environments):

```bash
# 1. Re-run bootstrap (will prompt to create new client)
./infrastructure/scripts/bootstrap-identity-platform.sh web-app-demo-root

# 2. Update root Terraform
cd infrastructure/root
terraform apply

# 3. Update environment Terraform (optional, picks up changes automatically)
cd infrastructure/env
terraform apply -var-file=../config/dev/terraform.tfvars
terraform apply -var-file=../config/prod/terraform.tfvars
```

All environments immediately use the new credentials.

## Troubleshooting

### "Cannot access secret"

**Problem**: Environment can't read secrets from root project

**Solution**: Grant the environment's service account access:
```bash
gcloud secrets add-iam-policy-binding google_oauth_client_id \
  --project=web-app-demo-root \
  --member="serviceAccount:github-actions@web-app-demo-dev.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

(This should be automated in root Terraform, but manual fix shown above)

### "API key not found"

**Problem**: Forgot to run post-terraform script

**Solution**: Run it now (using any configured environment):
```bash
./infrastructure/scripts/post-terraform-identity-platform.sh web-app-demo-dev web-app-demo-root
```

### "Different OAuth clients per environment?"

**Question**: What if I want separate OAuth clients for dev/prod?

**Answer**: Not recommended with this architecture, but possible:
1. Create additional OAuth clients in root
2. Store them as `google_oauth_client_id_prod`, etc.
3. Update environment Terraform to reference environment-specific secrets

However, this defeats the purpose of centralization. Better to use the same client across environments.

## Security Considerations

### Shared Credentials
- Same OAuth client used across all environments
- Acceptable for internal/development applications  
- For production with strict security: use separate OAuth clients per environment

### Secret Access
- Root project secrets accessible to all environment service accounts
- Use IAM to restrict which environments can access which secrets
- Audit logs track all secret access

### Best Practices
1. Use root project **only** for shared resources
2. Grant least privilege to environment service accounts
3. Rotate credentials regularly (every 90 days)
4. Monitor secret access via Cloud Audit Logs
5. For production: consider environment-specific OAuth clients

## Summary

**Before** (per-environment bootstrap):
- Run bootstrap script for dev
- Run bootstrap script for staging  
- Run bootstrap script for prod
- Manage 3 sets of OAuth credentials
- 3 separate tfvars files with secrets

**After** (centralized root bootstrap):
- Run bootstrap script **once** for root
- All environments use same credentials
- Simple tfvars files (no secrets)
- Single source of truth
- Much easier to manage

## Support

For issues:
- Review root Terraform: `infrastructure/root/gcp_identity_platform.tf`
- Review env Terraform: `infrastructure/env/gcp_identity_platform.tf`
- Check workflows: `.github/workflows/push-commit.yaml`
- Check secrets: `gcloud secrets list --project=web-app-demo-root`
