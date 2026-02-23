resource "google_identity_platform_config" "default" {
  depends_on = [google_project_service.env_services]

  project = var.project_id

  sign_in {
    allow_duplicate_emails = false
  }

  # Authorized domains include localhost and backend/frontend Cloud Run URLs
  authorized_domains = concat(
    ["localhost"],
    [replace(google_cloud_run_v2_service.backend.uri, "https://", "")],
    [replace(google_cloud_run_v2_service.frontend.uri, "https://", "")]
  )
}

resource "google_identity_platform_default_supported_idp_config" "google" {
  depends_on = [google_identity_platform_config.default]

  project = var.project_id
  idp_id  = "google.com"
  enabled = true

  client_id     = var.google_oauth_client_id
  client_secret = var.google_oauth_client_secret
}

# Store OAuth credentials in Secret Manager for GitHub Actions
resource "google_secret_manager_secret" "google_oauth_client_id" {
  project   = var.project_id
  secret_id = "google_oauth_client_id"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "google_oauth_client_id_v1" {
  secret      = google_secret_manager_secret.google_oauth_client_id.id
  secret_data = google_identity_platform_default_supported_idp_config.google.client_id
}

resource "google_secret_manager_secret" "google_oauth_client_secret" {
  project   = var.project_id
  secret_id = "google_oauth_client_secret"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "google_oauth_client_secret_v1" {
  secret      = google_secret_manager_secret.google_oauth_client_secret.id
  secret_data = var.google_oauth_client_secret
}

# Store Identity Platform API key in Secret Manager
# This will be populated after Identity Platform creates the API key
resource "google_secret_manager_secret" "identity_platform_api_key" {
  project   = var.project_id
  secret_id = "identity_platform_api_key"

  replication {
    auto {}
  }

  depends_on = [google_identity_platform_config.default]
}
