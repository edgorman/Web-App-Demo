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
- **Cloud Run Services**: Serverless container deployments for the backend and other services
- **IAM Policies**: Access control for service invocation
- **Configuration**: Environment-specific variables and scaling settings

See [Backend Service Deployment](../services/backend-deployment.md) for details on the backend Cloud Run service.

## Security Model
- **Workload Identity Federation**: No long-lived GCP service account keys are used. GitHub Actions authenticates via OIDC.
- **Least Privilege**: The GitHub Actions service account is granted `Editor` access across the projects, with specific `Secret Accessor` roles for sensitive values.
