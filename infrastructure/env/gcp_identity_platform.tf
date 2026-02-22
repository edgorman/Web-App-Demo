resource "google_identity_platform_config" "default" {
  depends_on = [google_project_service.env_services]

  project = var.project_id

  sign_in {
    allow_duplicate_emails = false
  }

  # Authorized domains will be updated via gcloud in GitHub Actions after Cloud Run deployment
  # Initial list includes localhost for local development
  authorized_domains = ["localhost"]

  lifecycle {
    ignore_changes = [
      authorized_domains
    ]
  }
}

resource "google_identity_platform_default_supported_idp_config" "providers" {
  for_each = var.identity_platform_providers

  depends_on = [google_identity_platform_config.default]

  project = var.project_id
  idp_id  = each.key
  enabled = each.value.enabled

  client_id     = each.value.client_id
  client_secret = each.value.client_secret
}
