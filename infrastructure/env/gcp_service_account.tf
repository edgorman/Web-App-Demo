# Service account for the backend Cloud Run service
# This replaces the default Compute Engine service account with minimal permissions
resource "google_service_account" "backend" {
  project      = var.project_id
  account_id   = "${var.backend_service_name}-sa"
  display_name = "Backend Cloud Run Service Account"
  description  = "Custom service account for the backend Cloud Run service with minimal IAM permissions"
}

# Note: No additional IAM role bindings are required for this service account
# as the backend service is a stateless FastAPI application that does not
# access any Google Cloud resources. The service account is used solely
# to run the Cloud Run service with the principle of least privilege.
