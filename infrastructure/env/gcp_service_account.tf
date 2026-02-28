# Service account for the backend Cloud Run service
# This replaces the default Compute Engine service account with minimal permissions
resource "google_service_account" "backend" {
  project      = var.project_id
  account_id   = "${var.backend_service_name}-sa"
  display_name = "Backend Cloud Run Service Account"
  description  = "Custom service account for the backend Cloud Run service with minimal IAM permissions"
}

# Service account for the frontend Cloud Run service
# This replaces the default Compute Engine service account with minimal permissions
resource "google_service_account" "frontend" {
  project      = var.project_id
  account_id   = "${var.frontend_service_name}-sa"
  display_name = "Frontend Cloud Run Service Account"
  description  = "Custom service account for the frontend Cloud Run service with minimal IAM permissions"
}

# Note: No additional IAM role bindings are required for these service accounts
# as both services are stateless applications that do not access any Google Cloud
# resources. The service accounts are used solely to run the Cloud Run services
# with the principle of least privilege.
