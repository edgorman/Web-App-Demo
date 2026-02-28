# Infrastructure Setup Guide

Follow these steps to initialize and configure the infrastructure for this project.

## 1. Prepare GitHub Repository
- **Create/Clone/Fork**: Start by creating a new repository or forking this one.
- **Local Clone**: Clone the repository to your local machine to begin configuration.

## 2. Create GitHub Personal Access Token (PAT)
Terraform requires a PAT to manage GitHub resources (variables, rulesets, etc.).
- Go to **GitHub Settings** > **Developer Settings** > **Personal Access Tokens**.
- Create a token with the following scopes:
    - `repo` (Full control of private repositories)
    - `workflow` (Required if managing actions)
    - `admin:repo_hook`
- Save this token securely; you will use it as a Terraform variable.

## 3. Create GCP Root Project
- Log in to the [GCP Console](https://console.cloud.google.com/).
- Create a new project that will serve as the **Root Project**.
- Note the **Project ID** (e.g., `my-project-root-123`).
- Ensure Billing is enabled for this project.
- **Note**: You do not need to create service account keys manually; the first manual apply will set up Workload Identity for GitHub.

## 4. Update Naming and Configuration
Update the following files in the repository to match your environment:
- **`infrastructure/root/variables.tf`**: Update the `default` values for:
    - `gcp_provider_project_id`: Your root project ID from Step 3.
    - `gcp_project_prefix`: The prefix for your dev/prod projects.
    - `github_repository_owner`: Your GitHub username or organization.
    - `github_repository_name`: Your repository name.
- **`infrastructure/config/root/terraform.tfvars`**: Alternatively, define these values here to keep code generic.

## 5. Bootstrap Infrastructure
Run the initial deployment from your local machine to set up the foundation:
```bash
cd infrastructure/root

# Initialize Terraform
terraform init

# Apply the configuration
# You will be prompted for the 'github_provider_token' created in Step 2
terraform apply
```
**What this does**:
- Enables required GCP APIs.
- Creates the Dev and Prod projects.
- Creates GCS buckets for remote state management.
- Sets up Workload Identity Federation.
- **Grants IAM Permissions**: Assigns Editor and Cloud Run Admin roles to the GitHub Actions service account on all environment projects.
- **Wires GitHub Variables**: Automatically populates `WORKLOAD_IDENTITY_PROVIDER` and `SERVICE_ACCOUNT` into your GitHub repository settings.

## 6. Start Making PRs
Once the bootstrap is complete, the GitHub CI/CD is fully functional. 
- You can now create a new branch, make changes to `infrastructure/env` or `infrastructure/root`, and open a Pull Request.
- The `pull-request` workflow will automatically run plans using the newly created identity.
- Merging to `develop` or `main` will trigger the `push-commit` workflow to apply changes.
