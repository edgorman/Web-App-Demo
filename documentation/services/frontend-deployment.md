# Frontend Service Deployment

This document describes the Cloud Run infrastructure for deploying the frontend service.

## Overview

The frontend service is a React + TypeScript (Vite) single-page app, built into static assets and served by nginx. It's containerized using Docker and deployed automatically through Terraform infrastructure as code. Because it's a static SPA, all backend calls are made directly from the end user's browser — nginx does not proxy `/api` requests.

## Architecture

### Cloud Run Service
- **Service Name**: `frontend` (configurable per environment)
- **Region**: `europe-west1` (default)
- **Container Port**: 8080
- **Image Source**: Google Artifact Registry

### Resource Configuration
- **CPU**: 1 vCPU
- **Memory**: 512 MiB
- **Min Instances**:
  - Dev: 0 (scales to zero for cost savings)
  - Prod: 0 (scales to zero for cost savings)
- **Max Instances**:
  - Dev: 5
  - Prod: 10

### Access Control
- **Public Access**: Allowed - `allUsers` has `roles/run.invoker`. The frontend is a static site with no server-side authentication of its own, so it's public by design — anyone who loads the page can then call the backend directly from their browser, subject to the backend's own CORS and application-layer auth.
- Unlike the backend, the frontend has no CORS allow-list or other application-layer access control — nginx serves static assets to anyone.

## Infrastructure Files

### Terraform Configuration
Located in `infrastructure/env/`:
- `gcp_cloud_run.tf` - Cloud Run service and IAM configuration
- `gcp_service_account.tf` - Custom service account for the frontend service
- `gcp_artifact_registry.tf` - Artifact Registry repository for frontend images
- `variables.tf` - Input variables
- `outputs.tf` - Service URL output
- `providers.tf` - Provider configuration

### Environment Configuration
Located in `infrastructure/config/`:
- `dev/terraform.tfvars` - Development environment settings
- `prod/terraform.tfvars` - Production environment settings

## Deployment Process

### Prerequisites

The following are automatically managed by Terraform:

1. **Artifact Registry repository**: Created in each environment (dev/prod) to store Docker images
2. **Required GCP APIs** (handled by environment infrastructure):
   - Cloud Run API (`run.googleapis.com`)
   - Artifact Registry API (`artifactregistry.googleapis.com`)

Container images are automatically built and pushed by GitHub Actions when frontend service files are changed.

### Manual Deployment

To manually deploy the frontend service:

```bash
cd infrastructure/env

# Switch to the desired environment (dev or prod)
make switch dev  # or 'make switch prod'

# Review the planned changes
terraform plan -var-file=../config/dev/terraform.tfvars

# Apply the changes
terraform apply -var-file=../config/dev/terraform.tfvars
```

### Automated Deployment

The frontend service is automatically deployed through GitHub Actions:
- **Infrastructure**: Changes to `infrastructure/env/` or environment config files trigger Terraform deployment workflows
- **Frontend Service**: Changes to `services/frontend/**` trigger Docker image build and Cloud Run deployment
- Merging to `develop` branch deploys to dev environment
- Merging to `main` branch deploys to prod environment
- The frontend deploy job (`frontend-dev`/`frontend-prod` in `.github/workflows/push-commit.yaml`) waits on the corresponding infrastructure and backend jobs, since it needs the deployed backend's URL as a build argument

#### Deployment Flow

When frontend service files are changed and pushed:

1. GitHub Actions detects changes in `services/frontend/**`
2. The backend's deployed Cloud Run URL is looked up (`.github/actions/get-service-url`)
3. The Docker image is built from the service code, with the backend URL and Google Sign-In client ID passed in as build args:
   - `VITE_BACKEND_URL` - the backend service's Cloud Run URL
   - `VITE_GOOGLE_CLIENT_ID` - the shared Google OAuth client ID (from the `GOOGLE_CLIENT_ID` GitHub Actions variable — see [Google Sign-In](google-sign-in.md))

   These are baked into the static build at build time (standard for a Vite SPA — there is no server-side runtime to read env vars from after the assets are built).
4. Image is pushed to Google Artifact Registry:
   - Dev: `europe-west1-docker.pkg.dev/web-app-demo-dev/frontend/frontend:${commit-sha}`
   - Prod: `europe-west1-docker.pkg.dev/web-app-demo-prod/frontend/frontend:${commit-sha}`
5. Cloud Run service is updated with the new image automatically

## Configuration Variables

### Required Variables
- `project_id` - GCP project ID for the environment
- `region` - GCP region for Cloud Run service
- `frontend_image` - Full container image path

### Optional Variables
- `frontend_service_name` - Name of the Cloud Run service (default: "frontend")
- `frontend_min_instances` - Minimum number of instances (default: 0)
- `frontend_max_instances` - Maximum number of instances (default: 10)

### Build-Time Variables
These are not Terraform variables — they're Docker build args baked into the static bundle by GitHub Actions (see [Deployment Flow](#deployment-flow) above):
- `VITE_BACKEND_URL` - backend API base URL
- `VITE_GOOGLE_CLIENT_ID` - Google OAuth client ID for the sign-in button

## Accessing the Service

The frontend service is reachable directly over HTTPS.

After deployment, the service URL is available as a Terraform output:

```bash
terraform output frontend_service_url
```

The URL will be in the format: `https://frontend-<hash>-<region>.run.app`

The page served at that URL calls the backend directly from the browser using the `VITE_BACKEND_URL` baked in at build time.

## Monitoring and Logs

### Cloud Console
- Navigate to Cloud Run in the GCP Console
- Select your project and the frontend service
- View metrics, logs, and revisions

### Command Line
```bash
# View service details
gcloud run services describe frontend --region=europe-west1

# Stream logs
gcloud run services logs read frontend --region=europe-west1 --follow
```

## Scaling Behavior

### Development Environment
- Scales to zero when idle (no traffic)
- First request after idle period may experience cold start (nginx starts quickly, so this is typically faster than the backend's)
- Cost-optimized for development and testing

### Production Environment
- Scales to zero when idle (no traffic)
- Automatically scales up to 10 instances under load
- Scales down gradually when traffic decreases

## Cost Considerations

Cloud Run pricing is based on:
1. **CPU and Memory**: Charged per 100ms of request processing
2. **Requests**: $0.40 per million requests
3. **Minimum Instances**: Charged continuously when > 0

Development and production environments both use `min_instances=0`, so costs are only incurred while serving traffic.

## Troubleshooting

### Common Issues

**Issue: Service won't start**
- Check container logs in Cloud Console
- Verify the container image exists in Artifact Registry
- Ensure nginx is listening on port 8080 (`nginx.conf`)

**Issue: Blank page or 404s on client-side routes**
- Confirm `nginx.conf`'s `location /` block still has `try_files $uri $uri/ /index.html;` — without this fallback, refreshing a client-side route 404s instead of loading the SPA shell.

**Issue: Frontend can't reach the backend / requests fail**
- Check the built assets were baked with the correct `VITE_BACKEND_URL`. Since this is set at build time, a wrong or empty value can't be fixed by changing an env var on the deployed Cloud Run revision — the image has to be rebuilt.
- If the browser reports a CORS error, check the backend's CORS allow-list rather than the frontend — see [Backend Service Deployment](backend-deployment.md#troubleshooting).

**Issue: "Google sign-in is not configured" message**
- The build was missing `VITE_GOOGLE_CLIENT_ID`. See [Google Sign-In](google-sign-in.md) for how the client ID is configured and wired into the frontend build.

## Security Considerations

### Current Configuration
- ✅ Container runs as a standard `nginx:alpine` image; static assets only, no server-side code execution
- ✅ HTTPS enforced (automatic with Cloud Run)
- ✅ Custom service account with minimal permissions (follows GCP best practices)
- ✅ Basic security headers set by nginx (`X-Frame-Options`, `X-Content-Type-Options`)
- ⚠️ Public at the Cloud Run IAM layer (`allUsers` → `roles/run.invoker`) — expected, since this is a public website
- ⚠️ No secrets are stored in the frontend image; the Google client ID baked into the bundle is not sensitive (it's a public OAuth client ID, not a secret)

### Service Account
The frontend service uses a dedicated custom service account (`frontend-sa`) instead of the default Compute Engine service account. This follows the principle of least privilege and GCP security best practices:
- No additional IAM role bindings are required as the frontend serves static assets only
- The service account is used solely to run the Cloud Run service
- This eliminates security warnings about using the default service account with broad IAM permissions

### Production Recommendations
1. Use Cloud Armor for DDoS protection
2. Enable a CDN in front of Cloud Run for static asset caching
3. Monitor and alert on suspicious access patterns
4. Regularly review and audit IAM permissions
