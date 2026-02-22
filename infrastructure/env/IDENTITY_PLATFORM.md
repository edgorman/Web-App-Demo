# Google Identity Platform Infrastructure

This directory contains Terraform configuration for deploying a "dirt cheap" frontend service on GCP with Google Identity Platform authentication.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    GCP Project                               │
│                                                              │
│  ┌──────────────────────────────────────────────────┐       │
│  │  Identity Platform (GCIP)                        │       │
│  │  - Google OAuth Provider                         │       │
│  │  - No Firebase SDK                               │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  ┌──────────────────────────────────────────────────┐       │
│  │  Cloud Run - Frontend Service                    │       │
│  │  - Scales to 0 (cost savings)                    │       │
│  │  - Pure OAuth2/OIDC redirect flow                │       │
│  │  - Static HTML/JS (nginx)                        │       │
│  │  - No database (JWT only)                        │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  ┌──────────────────────────────────────────────────┐       │
│  │  Cloud Run - Backend Service                     │       │
│  │  - Scales to 0 (cost savings)                    │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## New Resources Added

### 1. Identity Platform Configuration (`gcp_identity_platform.tf`)

- **google_identity_platform_config**: Enables and configures Identity Platform
  - Prevents duplicate emails
  - Configures authorized domains for OAuth redirects
  
- **google_identity_platform_default_supported_idp_config**: Configures Google as OAuth provider
  - Requires OAuth Client ID and Secret
  - Enables Google sign-in

### 2. Frontend Cloud Run Service (`gcp_cloud_run.tf`)

- **google_cloud_run_v2_service.frontend**: Frontend service deployment
  - Scales to 0 for cost savings
  - Serves static OAuth login page
  - Public access enabled
  - Image managed by CI/CD

### 3. Enabled Services (`gcp_services.tf`)

Added:
- `identitytoolkit.googleapis.com` - Identity Platform/Toolkit API

## Configuration

### Required Variables

Add to `config/dev/terraform.tfvars` or `config/prod/terraform.tfvars`:

```hcl
# OAuth Configuration (from GCP Console)
google_oauth_client_id     = "YOUR_CLIENT_ID.apps.googleusercontent.com"
google_oauth_client_secret = "YOUR_CLIENT_SECRET"

# Authorized domains for OAuth redirects
identity_platform_authorized_domains = [
  "localhost",
  "your-frontend-service-xyz.run.app"
]

# Frontend service configuration (optional, defaults provided)
frontend_service_name  = "frontend"
frontend_image         = "us-docker.pkg.dev/cloudrun/container/hello"
frontend_port          = 8080
frontend_cpu           = "1"
frontend_memory        = "512Mi"
frontend_min_instances = 0  # Scale to 0 for cost savings
frontend_max_instances = 10
```

### Outputs

After deployment, Terraform provides:

- `backend_service_url` - Backend Cloud Run URL
- `frontend_service_url` - Frontend Cloud Run URL (configure in OAuth console)
- `identity_platform_api_key` - Link to get Web API Key

## Deployment Steps

### Step 1: Create OAuth Credentials

1. Go to [GCP Console - Credentials](https://console.cloud.google.com/apis/credentials)
2. Create OAuth 2.0 Client ID (Web application)
3. Configure authorized origins and redirect URIs
4. Save Client ID and Secret

### Step 2: Configure Variables

```bash
cd infrastructure/config/dev
# Edit terraform.tfvars with your OAuth credentials
```

### Step 3: Deploy Infrastructure

```bash
cd infrastructure/env
make switch dev
terraform init
terraform plan
terraform apply
```

### Step 4: Update OAuth Redirect URIs

After deployment:
1. Note the frontend Cloud Run URL
2. Update OAuth client in GCP Console
3. Add the Cloud Run URL to authorized origins and redirect URIs

## Cost Optimization Features

1. **Scale to Zero**: Both services scale to 0 when not in use
   - No compute charges when idle
   - Cold start latency on first request

2. **No Database**: JWT is the only source of truth
   - No Cloud SQL costs
   - No Firestore costs
   - No data storage costs

3. **Minimal Resources**: 
   - CPU: 1 vCPU
   - Memory: 512Mi
   - Sufficient for static frontend

4. **Efficient Static Serving**: nginx alpine image
   - Small image size (~25MB)
   - Fast startup time
   - Low memory footprint

## Security Considerations

1. **Sensitive Variables**: OAuth secrets marked as sensitive
2. **Public Access**: Both services allow public access (required for OAuth)
3. **HTTPS Only**: Cloud Run enforces HTTPS
4. **State Parameter**: OAuth flow includes CSRF protection
5. **Token Validation**: Frontend validates token expiry

## Terraform Resources

### New Files

- `gcp_identity_platform.tf` - Identity Platform configuration
- Updated `gcp_services.tf` - Added Identity Toolkit API
- Updated `gcp_cloud_run.tf` - Added frontend service
- Updated `variables.tf` - Added frontend and OAuth variables
- Updated `outputs.tf` - Added frontend URL and API key info

### Dependencies

```
google_project_service.env_services
  ↓
google_identity_platform_config.default
  ↓
google_identity_platform_default_supported_idp_config.google

google_project_service.env_services
  ↓
google_cloud_run_v2_service.frontend
  ↓
google_cloud_run_v2_service_iam_member.frontend_public_access
```

## Cleanup

To destroy resources:

```bash
cd infrastructure/env
terraform destroy
```

Note: This will delete the Identity Platform configuration and Cloud Run services.

## References

- [Google Identity Platform Documentation](https://cloud.google.com/identity-platform/docs)
- [OAuth 2.0 for Web Server Applications](https://developers.google.com/identity/protocols/oauth2/web-server)
- [Cloud Run Pricing](https://cloud.google.com/run/pricing)
