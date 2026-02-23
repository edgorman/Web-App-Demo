# Google Identity Platform Configuration (Root)
# This is configured once in the root project and shared across all environments
# Each environment will configure its own authorized domains

# Enable Identity Platform API in root project
resource "google_project_service" "identity_platform" {
  project = var.gcp_provider_project_id
  service = "identitytoolkit.googleapis.com"

  disable_on_destroy = false
}

# Create OAuth client credentials secrets
# These are shared across all environments
resource "google_secret_manager_secret" "google_oauth_client_id" {
  project   = var.gcp_provider_project_id
  secret_id = "google_oauth_client_id"

  replication {
    auto {}
  }

  depends_on = [google_project_service.identity_platform]
}

resource "google_secret_manager_secret_version" "google_oauth_client_id_v1" {
  secret      = google_secret_manager_secret.google_oauth_client_id.id
  secret_data = var.google_oauth_client_id
}

resource "google_secret_manager_secret" "google_oauth_client_secret" {
  project   = var.gcp_provider_project_id
  secret_id = "google_oauth_client_secret"

  replication {
    auto {}
  }

  depends_on = [google_project_service.identity_platform]
}

resource "google_secret_manager_secret_version" "google_oauth_client_secret_v1" {
  secret      = google_secret_manager_secret.google_oauth_client_secret.id
  secret_data = var.google_oauth_client_secret
}

# Identity Platform API Key secret
# Will be populated after Identity Platform is configured in an environment
resource "google_secret_manager_secret" "identity_platform_api_key" {
  project   = var.gcp_provider_project_id
  secret_id = "identity_platform_api_key"

  replication {
    auto {}
  }

  depends_on = [google_project_service.identity_platform]
}

# Grant GitHub Actions service account access to OAuth secrets
resource "google_secret_manager_secret_iam_member" "github_oauth_client_id_accessor" {
  project   = var.gcp_provider_project_id
  secret_id = google_secret_manager_secret.google_oauth_client_id.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.github_actions.email}"
}

resource "google_secret_manager_secret_iam_member" "github_oauth_client_secret_accessor" {
  project   = var.gcp_provider_project_id
  secret_id = google_secret_manager_secret.google_oauth_client_secret.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.github_actions.email}"
}

resource "google_secret_manager_secret_iam_member" "github_identity_platform_api_key_accessor" {
  project   = var.gcp_provider_project_id
  secret_id = google_secret_manager_secret.identity_platform_api_key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.github_actions.email}"
}
