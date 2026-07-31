output "backend_service_url" {
  description = "The URL of the backend Cloud Run service"
  value       = google_cloud_run_v2_service.backend.uri
}

output "frontend_service_url" {
  description = "The URL of the frontend Cloud Run service"
  value       = google_cloud_run_v2_service.frontend.uri
}

output "firestore_database_name" {
  description = "The name of the Firestore database"
  value       = google_firestore_database.database.name
}
