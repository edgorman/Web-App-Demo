# Infrastructure Bootstrap Scripts

This directory contains scripts to automate the setup of Google Identity Platform and OAuth credentials for new environments.

## Overview

The bootstrap process has been automated to eliminate manual steps and avoid the chicken-and-egg problem with OAuth credentials and Identity Platform configuration.

## Quick Start

### For a New Environment

Run these commands in order:

```bash
# 1. Bootstrap Identity Platform (creates OAuth cred credentials and secrets)
./infrastructure/scripts/bootstrap-identity-platform.sh <project-id> <environment>

# 2. Apply Terraform configuration
cd infrastructure/env
terraform init
terraform apply -var-file=../config/<environment>/terraform.tfvars

# 3. Retrieve and store API key
cd ../..
./infrastructure/scripts/post-terraform-identity-platform.sh <project-id> <environment>
```

### Example: Setting up Dev Environment

```bash
# Bootstrap
./infrastructure/scripts/bootstrap-identity-platform.sh web-app-demo-dev dev

# Terraform
cd infrastructure/env
terraform init
terraform apply -var-file=../config/dev/terraform.tfvars

# Post-Terraform
cd ../..
./infrastructure/scripts/post-terraform-identity-platform.sh web-app-demo-dev dev
```

## Script Details

### 1. bootstrap-identity-platform.sh

**Purpose**: Automates OAuth client creation and initial Secret Manager setup

**What it does**:
- Enables required GCP APIs (Identity Platform, Secret Manager, IAP)
- Creates OAuth consent screen (brand) if it doesn't exist
- Creates OAuth client credentials for Identity Platform
- Stores OAuth credentials in Secret Manager
- Creates placeholder for Identity Platform API key
- Generates `terraform.tfvars` file with credentials

**Usage**:
```bash
./bootstrap-identity-platform.sh <project-id> [environment]
```

**Arguments**:
- `project-id` (required): GCP project ID (e.g., web-app-demo-dev)
- `environment` (optional): Environment name (default: dev)

**Output**:
- Secret Manager secrets:
  - `google_oauth_client_id`
  - `google_oauth_client_secret`
  - `identity_platform_api_key` (placeholder)
- File: `infrastructure/config/<environment>/terraform.tfvars`

**Prerequisites**:
- `gcloud` CLI installed and authenticated
- Project creator or owner permissions
- `jq` installed for JSON parsing

### 2. post-terraform-identity-platform.sh

**Purpose**: Retrieves Identity Platform API key after Terraform creates the configuration

**What it does**:
- Retrieves the auto-created Identity Platform API key
- Updates the `identity_platform_api_key` secret in Secret Manager
- Validates the key is stored correctly

**Usage**:
```bash
./post-terraform-identity-platform.sh <project-id> [environment]
```

**Arguments**:
- `project-id` (required): GCP project ID
- `environment` (optional): Environment name (default: dev)

**Prerequisites**:
- Terraform has been successfully applied
- Identity Platform configuration exists

## Why This Approach?

### The Problem

Previously, bootstrapping a new environment required:
1. Manually creating OAuth credentials in GCP Console
2. Manually copying client ID and secret
3. Running Terraform with variables
4. Manually retrieving Identity Platform API key
5. Manually adding API key to Secret Manager

This was error-prone and time-consuming.

### The Solution

The bootstrap scripts automate all of this:
- OAuth credentials are created programmatically via `gcloud`
- All secrets are automatically stored in Secret Manager
- Terraform variables file is auto-generated
- API key retrieval is automated post-Terraform

## Secrets Management

All secrets are stored in Google Secret Manager:

| Secret Name | Description | Created By |
|------------|-------------|------------|
| `google_oauth_client_id` | OAuth 2.0 Client ID | bootstrap script |
| `google_oauth_client_secret` | OAuth 2.0 Client Secret | bootstrap script |
| `identity_platform_api_key` | Identity Platform Web API Key | post-terraform script |

## CI/CD Integration

GitHub Actions workflows automatically read these secrets from Secret Manager during deployment:

```yaml
- name: Get OAuth Client ID
  run: |
    CLIENT_ID=$(gcloud secrets versions access latest \
      --secret="google_oauth_client_id" \
      --project="${{ inputs.project_id }}")
    echo "TF_VAR_google_oauth_client_id=$CLIENT_ID" >> $GITHUB_ENV
```

This ensures:
- No secrets in version control
- Secrets are environment-specific
- Automated deployments work seamlessly

## Terraform Integration

The Terraform configuration uses these secrets through variables:

```hcl
variable "google_oauth_client_id" {
  description = "Google OAuth 2.0 Client ID for Identity Platform"
  type        = string
  sensitive   = true
}
```

During CI/CD, these are injected as environment variables:
- `TF_VAR_google_oauth_client_id`
- `TF_VAR_google_oauth_client_secret`

## Troubleshooting

### "Brand already exists" error

This is normal if you've run the script before. The script will use the existing brand.

### "Cannot retrieve client secret"

OAuth client secrets cannot be retrieved after creation. If you lose the secret:
1. Create a new OAuth client (script will prompt you)
2. Or manually provide the secret when prompted

### "API key not found"

The API key is created when Terraform configures Identity Platform. If the post-terraform script can't find it:
1. Check that Terraform apply completed successfully
2. Manually retrieve the key from GCP Console → APIs & Credentials
3. Paste it when prompted by the script

### Permission Errors

Ensure your gcloud user has these roles:
- Project Owner or Editor
- Secret Manager Admin
- Identity Platform Admin

## Re-running Scripts

### Safe to Re-run

Both scripts are idempotent and safe to re-run:
- They check for existing resources before creating
- They update existing secrets with new versions
- They won't duplicate OAuth clients

### When to Re-run

**Bootstrap script**: Run again if you need to create a new OAuth client or rotate credentials

**Post-Terraform script**: Run after any Terraform changes that might affect the API key

## Manual Cleanup

To remove Identity Platform configuration:

```bash
# Delete Terraform resources
cd infrastructure/env
terraform destroy -var-file=../config/<environment>/terraform.tfvars

# Delete secrets (optional)
gcloud secrets delete google_oauth_client_id --project=<project-id>
gcloud secrets delete google_oauth_client_secret --project=<project-id>
gcloud secrets delete identity_platform_api_key --project=<project-id>

# Delete OAuth client (optional)
# This must be done via GCP Console
```

## Security Best Practices

1. **Never commit secrets**: The scripts store everything in Secret Manager
2. **Use separate OAuth clients per environment**: Dev, staging, and prod should have different credentials
3. **Rotate credentials regularly**: Re-run bootstrap script with new clients
4. **Audit access**: Monitor Secret Manager access logs
5. **Least privilege**: Grant minimal permissions to service accounts

## Next Steps

After running these scripts:

1. Configure authorized domains in `gcp_identity_platform.tf` if needed
2. Deploy frontend and backend services via CI/CD
3. Test OAuth login flow
4. Monitor Identity Platform metrics in GCP Console

## Support

For issues or questions:
- Check the troubleshooting section above
- Review Terraform plan output for configuration issues
- Check GCP Console → Identity Platform for configuration status
