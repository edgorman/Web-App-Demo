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
- **Grants IAM Permissions**: Assigns the `roles/admin` role to the GitHub Actions service account on all environment projects.
- **Wires GitHub Variables**: Automatically populates `WORKLOAD_IDENTITY_PROVIDER` and `SERVICE_ACCOUNT` into your GitHub repository settings.

## 6. Configure the Google Sign-In Client
The frontend's "Sign in with Google" button needs an OAuth 2.0 client ID, defined once in the root project and reused by both dev and prod.
- Follow [Google Sign-In](../services/google-sign-in.md) end-to-end: create the OAuth client ID in the `web-app-demo-root` GCP project's [credentials page](https://console.cloud.google.com/apis/credentials), then set `google_client_id` in `infrastructure/root/variables.tf` (or `infrastructure/config/root/terraform.tfvars`) and re-apply `infrastructure/root`.
- That apply wires the client ID into a `GOOGLE_CLIENT_ID` GitHub Actions repository variable, which CI then passes to both the backend and frontend builds for dev and prod automatically — no further per-environment configuration is needed.
- This step can be done any time after the bootstrap in Step 5, since it requires the root project (and its credentials page) to already exist.

## 7. Start Making PRs
Once the bootstrap is complete, the GitHub CI/CD is fully functional. 
- You can now create a new branch, make changes to `infrastructure/env` or `infrastructure/root`, and open a Pull Request.
- The `pull-request` workflow will automatically run plans using the newly created identity.
- Merging to `develop` or `main` will trigger the `push-commit` workflow to apply changes.
