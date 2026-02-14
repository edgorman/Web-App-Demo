resource "google_cloud_run_v2_service" "backend" {
  depends_on = [google_project_service.env_services]

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
  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

resource "google_cloud_run_v2_service_iam_member" "backend_public_access" {
  depends_on = [google_cloud_run_v2_service.backend]

  name     = google_cloud_run_v2_service.backend.name
  location = google_cloud_run_v2_service.backend.location
  project  = google_cloud_run_v2_service.backend.project
  role     = "roles/run.invoker"
  member   = "allUsers"
}
