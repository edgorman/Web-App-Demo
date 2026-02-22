# OAuth Client ID and Secret for Identity Platform
resource "google_secret_manager_secret" "google_oauth_client_id" {
  project   = var.project_id
  secret_id = "google_oauth_client_id"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "google_oauth_client_id_v1" {
  secret      = google_secret_manager_secret.google_oauth_client_id.id
  secret_data = var.google_oauth_client_id
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
