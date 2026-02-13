output "backend_service_url" {
  description = "The URL of the backend Cloud Run service"
  value       = google_cloud_run_v2_service.backend.uri
}

output "backend_service_name" {
  description = "The name of the backend Cloud Run service"
  value       = google_cloud_run_v2_service.backend.name
}
