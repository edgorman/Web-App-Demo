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

Note: Project-level IAM permissions for the GitHub Actions service account are managed centrally in the root project (`infrastructure/root/github_cicd.tf`).

### Access Control Model

The infrastructure implements a secure access control model for Cloud Run services:

- **Frontend Service**: Publicly accessible (`allUsers` has `roles/run.invoker`)
- **Backend Service**: Also reachable by `allUsers` at the Cloud Run IAM layer, because the frontend calls it directly from the user's browser. Access is constrained at the application layer instead, by the FastAPI CORS allow-list.

The frontend is a static single-page app: nginx serves the built assets and does
not proxy API requests, so `fetch` calls run in the end user's browser with no
GCP credentials. Cloud Run IAM therefore cannot distinguish them from any other
anonymous request, and an `allUsers` → `roles/run.invoker` binding on the backend
is required for the frontend to work at all. Removing it makes every browser call
fail with a 403 that has no CORS headers, which shows up in the browser as a CORS
error.

The backend's `roles/run.invoker` binding for the frontend service account is
retained for genuine server-side calls, but it is not what authorises the
browser traffic described above.

If the backend must not be publicly reachable, the frontend has to stop calling
it from the browser — e.g. by having nginx proxy `/api` and attaching an identity
token, or by putting both services behind a load balancer with IAP.

See [Backend Service Deployment](../services/backend-deployment.md) and [Frontend Service Deployment](../services/frontend-deployment.md) for details on each Cloud Run service.

## Security Model
- **Workload Identity Federation**: No long-lived GCP service account keys are used. GitHub Actions authenticates via OIDC.
- **Least Privilege**: The GitHub Actions service account is created in the root project, and the root project grants it the `roles/admin` role on all environment projects (root, dev, prod). This role is required to manage IAM policies for Cloud Run services, such as configuring service-to-service invocation. This centralized permission management ensures that the service account has the necessary permissions before Terraform attempts to manage resources in environment projects.
- **Cloud Run Service Accounts**: Each Cloud Run service uses a custom service account instead of the default Compute Engine service account. This follows GCP best practices and the principle of least privilege by ensuring each service has only the minimum permissions required for its operation.
