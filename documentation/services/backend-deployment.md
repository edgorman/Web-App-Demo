# Backend Service Deployment

This document describes the Cloud Run infrastructure for deploying the backend service.

## Overview

The backend service is a FastAPI application deployed to Google Cloud Run. It's containerized using Docker and deployed automatically through Terraform infrastructure as code.

## Architecture

### Cloud Run Service
- **Service Name**: `backend` (configurable per environment)
- **Region**: `europe-west1` (default)
- **Container Port**: 8000
- **Image Source**: Google Artifact Registry

### Resource Configuration
- **CPU**: 1 vCPU
- **Memory**: 512 MiB
- **Min Instances**: 
  - Dev: 0 (scales to zero for cost savings)
  - Prod: 1 (keeps warm instance to avoid cold starts)
- **Max Instances**:
  - Dev: 5
  - Prod: 10

### Access Control
The backend service is configured with public access (`allUsers` invoker role) for demo purposes. For production deployments with sensitive data, consider implementing:
- Cloud Run's built-in authentication
- API Gateway with API keys
- Application-level authentication (OAuth, JWT, etc.)

## Infrastructure Files

### Terraform Configuration
Located in `infrastructure/env/`:
- `gcp_cloud_run.tf` - Cloud Run service and IAM configuration
- `gcp_service_account.tf` - Custom service account for the backend service
- `variables.tf` - Input variables
- `outputs.tf` - Service URL, name, and service account outputs
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

Container images are automatically built and pushed by GitHub Actions when backend service files are changed.

### Manual Deployment

To manually deploy the backend service:

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

The backend service is automatically deployed through GitHub Actions:
- **Infrastructure**: Changes to `infrastructure/env/` or environment config files trigger Terraform deployment workflows
- **Backend Service**: Changes to `services/backend/**` trigger Docker image build and Cloud Run deployment
- Merging to `develop` branch deploys to dev environment
- Merging to `main` branch deploys to prod environment

#### Deployment Flow

When backend service files are changed and pushed:

1. GitHub Actions detects changes in `services/backend/**`
2. Docker image is built from the service code
3. Image is pushed to Google Artifact Registry:
   - Dev: `europe-west1-docker.pkg.dev/web-app-demo-dev/backend/backend:${commit-sha}`
   - Prod: `europe-west1-docker.pkg.dev/web-app-demo-prod/backend/backend:${commit-sha}`
4. Cloud Run service is updated with the new image automatically

## Configuration Variables

### Required Variables
- `project_id` - GCP project ID for the environment
- `region` - GCP region for Cloud Run service
- `backend_image` - Full container image path

### Optional Variables
- `backend_service_name` - Name of the Cloud Run service (default: "backend")
- `backend_min_instances` - Minimum number of instances (default: 0)
- `backend_max_instances` - Maximum number of instances (default: 10)

## Accessing the Service

After deployment, the service URL is available as a Terraform output:

```bash
terraform output backend_service_url
```

The URL will be in the format: `https://backend-<hash>-<region>.run.app`

## Monitoring and Logs

### Cloud Console
- Navigate to Cloud Run in the GCP Console
- Select your project and the backend service
- View metrics, logs, and revisions

### Command Line
```bash
# View service details
gcloud run services describe backend --region=europe-west1

# Stream logs
gcloud run services logs read backend --region=europe-west1 --follow
```

## Scaling Behavior

### Development Environment
- Scales to zero when idle (no traffic)
- First request after idle period may experience cold start (~2-5 seconds)
- Cost-optimized for development and testing

### Production Environment
- Scales to zero when idle (no traffic)
- First request after idle period may experience cold start (~2-5 seconds)
- Automatically scales up to 10 instances under load
- Scales down gradually when traffic decreases

## Cost Considerations

Cloud Run pricing is based on:
1. **CPU and Memory**: Charged per 100ms of request processing
2. **Requests**: $0.40 per million requests
3. **Minimum Instances**: Charged continuously when > 0

Development environment with min_instances=0 only incurs costs during active use. Production now also uses min_instances=0 to minimize costs and only incurs charges during active use.

## Troubleshooting

### Common Issues

**Issue: Service won't start**
- Check container logs in Cloud Console
- Verify the container image exists in Artifact Registry
- Ensure the container listens on port 8000

**Issue: 403 Forbidden**
- Verify the IAM policy allows public access
- Check that the service is deployed and healthy

**Issue: Cold starts taking too long**
- Consider increasing `backend_min_instances` in tfvars
- Optimize container startup time
- Use a smaller base image

## Security Considerations

### Current Configuration
- ✅ Container runs as non-root user (configured in Dockerfile)
- ✅ HTTPS enforced (automatic with Cloud Run)
- ✅ Custom service account with minimal permissions (follows GCP best practices)
- ⚠️ Public access enabled for demo purposes

### Service Account
The backend service uses a dedicated custom service account (`backend-sa`) instead of the default Compute Engine service account. This follows the principle of least privilege and GCP security best practices:
- No additional IAM role bindings are required as the backend is a stateless FastAPI application
- The service account is used solely to run the Cloud Run service
- This eliminates security warnings about using the default service account with broad IAM permissions

### Production Recommendations
1. Implement authentication at the application or infrastructure level
2. Use Cloud Armor for DDoS protection
3. Enable VPC egress controls if accessing internal services
4. Implement rate limiting
5. Use Cloud Run IAM for service-to-service authentication
