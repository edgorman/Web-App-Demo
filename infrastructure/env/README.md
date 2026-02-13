# Environment Infrastructure

This directory contains Terraform configuration for environment-specific resources (dev and prod).

## What's Deployed Here

### Cloud Run Services
- **Backend Service**: FastAPI application running in a serverless container
  - Configured for autoscaling (0-10 instances based on environment)
  - Public access enabled for demo purposes
  - See [Backend Deployment Documentation](../../documentation/services/backend-deployment.md) for details

## Configuration

### Files
- `providers.tf` - Terraform and provider configuration
- `variables.tf` - Input variables for the environment resources
- `gcp_cloud_run.tf` - Cloud Run service definitions
- `outputs.tf` - Exported values (service URLs, etc.)

### Environment-Specific Values
Configuration values are stored in `../config/<env>/terraform.tfvars`:
- `../config/dev/terraform.tfvars` - Development environment
- `../config/prod/terraform.tfvars` - Production environment

## Usage

### Initialize Terraform
Switch to a specific environment:
```bash
make switch dev   # or 'make switch prod'
```

This will run `terraform init` with the appropriate backend configuration.

### Plan Changes
```bash
terraform plan -var-file=../config/dev/terraform.tfvars
```

### Apply Changes
```bash
terraform apply -var-file=../config/dev/terraform.tfvars
```

## Deployment

Changes to this directory are automatically deployed via GitHub Actions:
- Push to `develop` branch → deploys to dev environment
- Push to `main` branch → deploys to prod environment

## Adding New Services

To add a new service:
1. Create a new `.tf` file for the service resources
2. Add required variables to `variables.tf`
3. Add outputs to `outputs.tf` if needed
4. Update environment tfvars files with service-specific values
5. Document the service in `documentation/services/`

## Prerequisites

Before deploying resources in this directory, ensure:
1. Root infrastructure has been deployed (`infrastructure/root/`)
2. Required APIs are enabled in the GCP projects
3. Container images are available in Artifact Registry (for Cloud Run services)
