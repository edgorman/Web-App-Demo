# Infrastructure Overview

This repository uses a multi-project GCP architecture managed by Terraform, designed for isolation and scalability.

## Architecture

The infrastructure is divided into three logical layers:

### 1. Root Project (`web-app-demo-root`)
Acts as the administrative hub for the entire stack.
- **State Management**: Hosts GCS buckets for Terraform states of all projects (root, dev, prod).
- **Identity & Security**: Contains the Workload Identity Federation resources and the central GitHub Actions Service Account.
- **Global Secrets**: Stores secrets shared across the stack, such as the `github_provider_token`.

### 2. Environment Projects (`web-app-demo-<env>`)
Isolated projects for application environments.
- Each environment has its own set of enabled APIs (Secret Manager, Cloud Run, Artifact Registry, etc.).
- Resource isolation ensures that testing in `dev` cannot affect the `prod` project.
- **Application Services**: Cloud Run services for deploying containerized applications (e.g., backend API).

## Unified Service Management
Services and APIs are managed via a consolidated `all_projects` local in Terraform. This ensures that every project in the stack has a consistent set of required APIs enabled (e.g., `secretmanager.googleapis.com`, `storage.googleapis.com`, `run.googleapis.com`, `artifactregistry.googleapis.com`).

## Application Infrastructure
The `infrastructure/env/` directory contains environment-specific resources:
- **Cloud Run Services**: Serverless container deployments for the backend and frontend services
- **Service IAM Policies**: Access control for individual service invocation
- **Configuration**: Environment-specific variables and scaling settings

Note: Project-level IAM permissions for the GitHub Actions service account are managed centrally in the root project (`infrastructure/root/gcp_env_iam.tf`).

### Access Control Model

The infrastructure implements a secure access control model for Cloud Run services:

- **Frontend Service**: Publicly accessible (`allUsers` has `roles/run.invoker`)
- **Backend Service**: Restricted access only to:
  - Frontend service account (for service-to-service communication)
  - Developers in the organization's Google Workspace domain (for testing/debugging)

This ensures the backend API is not publicly accessible and can only be invoked by authorized entities. The `developers_domain` variable must be configured in `terraform.tfvars` for each environment.

See [Backend Service Deployment](../services/backend-deployment.md) for details on the backend Cloud Run service.

## Security Model
- **Workload Identity Federation**: No long-lived GCP service account keys are used. GitHub Actions authenticates via OIDC.
- **Least Privilege**: The GitHub Actions service account is created in the root project, and the root project grants it `Editor` and `Cloud Run Admin` roles on all environment projects. The `Cloud Run Admin` role is required to manage IAM policies for Cloud Run services, such as enabling public access. This centralized permission management ensures that the service account has the necessary permissions before Terraform attempts to manage resources in environment projects.
- **Cloud Run Service Accounts**: Each Cloud Run service uses a custom service account instead of the default Compute Engine service account. This follows GCP best practices and the principle of least privilege by ensuring each service has only the minimum permissions required for its operation.
