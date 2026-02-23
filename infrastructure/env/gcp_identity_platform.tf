# Google Identity Platform Configuration (Environment-Specific)
# OAuth credentials are stored in root project and accessed here
# Each environment configures its own Identity Platform instance with environment-specific authorized domains

# Data sources to read OAuth credentials from root project Secret Manager
data "google_secret_manager_secret_version" "google_oauth_client_id" {
  project = var.root_project_id
  secret  = "google_oauth_client_id"
}

data "google_secret_manager_secret_version" "google_oauth_client_secret" {
  project = var.root_project_id
  secret  = "google_oauth_client_secret"
}

# Configure Identity Platform for this environment
resource "google_identity_platform_config" "default" {
  depends_on = [google_project_service.env_services]

  project = var.project_id

  sign_in {
    allow_duplicate_emails = false
  }

  # Authorized domains include localhost and this environment's Cloud Run URLs
  authorized_domains = concat(
    ["localhost"],
    [replace(google_cloud_run_v2_service.backend.uri, "https://", "")],
    [replace(google_cloud_run_v2_service.frontend.uri, "https://", "")]
  )
}

# Configure Google as OAuth provider using credentials from root project
resource "google_identity_platform_default_supported_idp_config" "google" {
  depends_on = [google_identity_platform_config.default]

  project = var.project_id
  idp_id  = "google.com"
  enabled = true

  # Use OAuth credentials from root project
  client_id     = data.google_secret_manager_secret_version.google_oauth_client_id.secret_data
  client_secret = data.google_secret_manager_secret_version.google_oauth_client_secret.secret_data
}
