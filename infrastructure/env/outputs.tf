output "backend_service_url" {
  description = "The URL of the backend Cloud Run service"
  value       = google_cloud_run_v2_service.backend.uri
}

output "backend_service_account" {
  description = "The email of the custom service account used by the backend Cloud Run service"
  value       = google_service_account.backend.email
}

output "frontend_service_url" {
  description = "The URL of the frontend Cloud Run service"
  value       = google_cloud_run_v2_service.frontend.uri
}
