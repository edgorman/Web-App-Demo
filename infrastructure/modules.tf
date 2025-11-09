module "core" {
  source = "./modules/core"

  gcp_project_id     = var.gcp_project_id
  gcp_default_region = var.gcp_default_region
  gcp_default_zone   = var.gcp_default_zone

  terraform_state_admins = var.admin_developers
}
