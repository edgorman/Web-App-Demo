module "core" {
  source = "./modules/core"

  gcp_project_id     = var.gcp_project_id
  gcp_default_region = var.gcp_default_region
  gcp_default_zone   = var.gcp_default_zone

  terraform_state_admins = [for email, user in var.developers : email if user.terraform_role == "admin"]
  
  github_access_token                            = var.github_access_token
  github_repository_admins                       = [for email, user in var.developers : user.github_username if user.github_role == "admin"]
  github_repository_developers                   = [for email, user in var.developers : user.github_username if user.github_role == "developer"]
  github_repository_viewers                      = [for email, user in var.developers : user.github_username if user.github_role == "viewer"]
  github_protected_branch                        = var.github_protected_branch
  github_protected_branch_require_admin_approval = var.environment == "production"
}
