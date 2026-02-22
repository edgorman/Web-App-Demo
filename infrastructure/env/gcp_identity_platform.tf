resource "google_identity_platform_config" "default" {
  depends_on = [google_project_service.env_services]

  project = var.project_id

  # Allow multiple accounts per email
  sign_in {
    allow_duplicate_emails = false
  }

  # Configure authorized domains for OAuth redirects
  authorized_domains = var.identity_platform_authorized_domains
}

resource "google_identity_platform_default_supported_idp_config" "google" {
  depends_on = [google_identity_platform_config.default]

  project = var.project_id
  idp_id  = "google.com"
  enabled = true

  client_id     = var.google_oauth_client_id
  client_secret = var.google_oauth_client_secret
}
