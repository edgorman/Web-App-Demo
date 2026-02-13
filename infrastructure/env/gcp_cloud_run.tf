resource "google_cloud_run_v2_service" "backend" {
  name     = var.backend_service_name
  location = var.region
  project  = var.project_id

  template {
    containers {
      image = var.backend_image

      ports {
        container_port = var.backend_port
      }

      resources {
        limits = {
          cpu    = var.backend_cpu
          memory = var.backend_memory
        }
      }
    }

    scaling {
      min_instance_count = var.backend_min_instances
      max_instance_count = var.backend_max_instances
    }
  }

  # Routes 100% of traffic to the latest revision.
  # This ensures all requests go to the most recently deployed version.
  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# Allow unauthenticated access to the backend service.
# CORS and authentication/authorization are implemented at the application level.
resource "google_cloud_run_v2_service_iam_member" "backend_public_access" {
  name     = google_cloud_run_v2_service.backend.name
  location = google_cloud_run_v2_service.backend.location
  project  = google_cloud_run_v2_service.backend.project
  role     = "roles/run.invoker"
  member   = "allUsers"
}
