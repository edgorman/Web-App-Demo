# CI/CD Overview

The CI/CD pipeline is designed to provide dynamic, automated infrastructure validation and deployment using GitHub Actions and Google Cloud Workload Identity Federation.

## Workflows

### 1. Pull Request (`pull-request.yaml`)
Triggered on PRs to `main` and `develop`.
- **Dynamic Diffing**: Uses a centralized diff action to determine which infrastructure components (root, dev, or prod) were modified.
- **Validation**: Performs `terraform init`, `fmt`, `validate`, and `plan` for the modified directories.
- **Cross-Environment Safety**: `dev` and `prod` plans run if environment files change, but they also wait for the `root` job if root files are modified in the same PR.

### 2. Push Commit (`push-commit.yaml`)
Triggered on merges to `main` and `develop`.
- **Automated Deployment**: Performs `terraform apply --auto-approve` for the changed infrastructure.
- **Identity Consistency**: Uses the same OIDC identity as the PR workflow to ensure that what was planned is what is applied.

## Custom Actions

To keep workflows clean and reusable, composite actions are used.

## Automated Variable Management
Terraform manages the GitHub environment itself. It automatically creates and updates GitHub Actions Variables (`WORKLOAD_IDENTITY_PROVIDER`, `SERVICE_ACCOUNT`, etc.) in the repository, ensuring the workflow always has the correct pointers to the GCP identity provider without manual configuration.
