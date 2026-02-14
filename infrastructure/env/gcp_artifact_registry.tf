resource "google_artifact_registry_repository" "backend" {
  depends_on = [google_project_service.env_services]

  location      = var.region
  repository_id = "backend"
  project       = var.project_id
  description   = "Docker repository for backend service images"
  format        = "DOCKER"

  docker_config {
    immutable_tags = false
  }
}
