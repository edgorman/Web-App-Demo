output "backend_service_url" {
  description = "The URL of the backend Cloud Run service"
  value       = google_cloud_run_v2_service.backend.uri
}

output "frontend_service_url" {
  description = "The URL of the frontend Cloud Run service"
  value       = google_cloud_run_v2_service.frontend.uri
}

output "identity_platform_api_key" {
  description = "The API key for Identity Platform (Web API Key from Firebase Console)"
  value       = "See GCP Console: https://console.cloud.google.com/customer-identity/providers?project=${var.project_id}"
}
