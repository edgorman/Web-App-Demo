module "gcp-projects" {
  source = "../../../packages/terraform/bootstrap/gcp-projects"

  gcp_root_project_id = var.gcp_root_project_id
  projects_base_id    = var.gcp_projects_base_id
  projects            = var.gcp_projects
}

module "github-repository" {
  source = "../../../packages/terraform/bootstrap/github-repository"

  provider_token  = var.github_provider_token
  admin_usernames = var.github_admin_usernames
  branches        = var.github_branches
}

module "terraform-states" {
  source = "../../../packages/terraform/bootstrap/terraform-states"

  gcp_project_id = var.gcp_root_project_id
  remote_states  = var.terraform_remote_states
  admin_emails   = var.terraform_admin_emails
  viewer_emails  = var.terraform_viewer_emails
}
