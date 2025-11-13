module "terraform-state" {
  source = "../packages/terraform/terraform-state"

  gcp_project_id     = var.gcp_project_id
  gcp_default_region = var.gcp_default_region
  gcp_default_zone   = var.gcp_default_zone

  terraform_state_admins = [for email, user in var.developers : email if user.terraform_role == "admin"]
}

module "github-repository" {
  source = "../packages/terraform/github-repository"

  github_provider_token                       = var.github_provider_token
  github_repository_admins                    = [for email, user in var.developers : user.github_username if user.github_role == "admin"]
  github_repository_developers                = [for email, user in var.developers : user.github_username if user.github_role == "developer"]
  github_repository_viewers                   = [for email, user in var.developers : user.github_username if user.github_role == "viewer"]
  github_target_branch                        = var.github_target_branch
  github_target_branch_require_admin_approval = var.environment == "production"
}
