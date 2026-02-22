resource "google_secret_manager_secret" "github_provider_token" {
  project   = var.gcp_provider_project_id
  secret_id = "github_provider_token"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "github_provider_token_v1" {
  secret      = google_secret_manager_secret.github_provider_token.id
  secret_data = var.github_provider_token
}

resource "google_secret_manager_secret_iam_member" "github_actions_secret_accessor" {
  project   = var.gcp_provider_project_id
  secret_id = google_secret_manager_secret.github_provider_token.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.github_actions.email}"
}

# OAuth Client ID and Secret for Identity Platform
resource "google_secret_manager_secret" "google_oauth_client_id" {
  project   = var.gcp_provider_project_id
  secret_id = "google_oauth_client_id"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "google_oauth_client_id_v1" {
  secret      = google_secret_manager_secret.google_oauth_client_id.id
  secret_data = var.google_oauth_client_id
}

resource "google_secret_manager_secret_iam_member" "google_oauth_client_id_accessor" {
  project   = var.gcp_provider_project_id
  secret_id = google_secret_manager_secret.google_oauth_client_id.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.github_actions.email}"
}

resource "google_secret_manager_secret" "google_oauth_client_secret" {
  project   = var.gcp_provider_project_id
  secret_id = "google_oauth_client_secret"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "google_oauth_client_secret_v1" {
  secret      = google_secret_manager_secret.google_oauth_client_secret.id
  secret_data = var.google_oauth_client_secret
}

resource "google_secret_manager_secret_iam_member" "google_oauth_client_secret_accessor" {
  project   = var.gcp_provider_project_id
  secret_id = google_secret_manager_secret.google_oauth_client_secret.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.github_actions.email}"
}
