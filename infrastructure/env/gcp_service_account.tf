# Service account for the backend Cloud Run service
# This replaces the default Compute Engine service account with minimal permissions
resource "google_service_account" "backend" {
  project      = var.project_id
  account_id   = "${var.backend_service_name}-sa"
  display_name = "Backend Cloud Run Service Account"
  description  = "Custom service account for the backend Cloud Run service with minimal IAM permissions"
}

# Grants the backend read/write access to Firestore, so it can persist and
# look up authenticated users (see services/backend/internal/storage/firestore/user.go).
resource "google_project_iam_member" "backend_firestore_access" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.backend.email}"
}

# Service account for the frontend Cloud Run service
# This replaces the default Compute Engine service account with minimal permissions
resource "google_service_account" "frontend" {
  project      = var.project_id
  account_id   = "${var.frontend_service_name}-sa"
  display_name = "Frontend Cloud Run Service Account"
  description  = "Custom service account for the frontend Cloud Run service with minimal IAM permissions"
}

# Note: The frontend service account has no additional IAM role bindings, as it
# is a stateless application that does not access any Google Cloud resources.
# The backend service account is granted `roles/datastore.user` above for its
# Firestore-backed user storage; both accounts otherwise run with the minimum
# permissions needed for their Cloud Run service.
