resource "google_cloud_run_v2_service" "backend" {
  depends_on = [google_project_service.env_services]

  name     = var.backend_service_name
  location = var.region
  project  = var.project_id

  template {
    service_account = google_service_account.backend.email

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

  # Ignore changes to the image after the service is created
  # as it will be updated via GitHub Actions
  lifecycle {
    ignore_changes = [
      template[0].containers[0].image
    ]
  }
}

# Grant frontend service account permission to invoke the backend
resource "google_cloud_run_v2_service_iam_member" "backend_frontend_access" {
  depends_on = [google_cloud_run_v2_service.backend]

  name     = google_cloud_run_v2_service.backend.name
  location = google_cloud_run_v2_service.backend.location
  project  = google_cloud_run_v2_service.backend.project
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.frontend.email}"
}

# Grant public access to invoke the backend
resource "google_cloud_run_v2_service_iam_member" "backend_public_access" {
  depends_on = [google_cloud_run_v2_service.backend]

  name     = google_cloud_run_v2_service.backend.name
  location = google_cloud_run_v2_service.backend.location
  project  = google_cloud_run_v2_service.backend.project
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_v2_service" "frontend" {
  depends_on = [google_project_service.env_services]

  name     = var.frontend_service_name
  location = var.region
  project  = var.project_id

  template {
    service_account = google_service_account.frontend.email

    containers {
      image = var.frontend_image

      ports {
        container_port = var.frontend_port
      }

      resources {
        limits = {
          cpu    = var.frontend_cpu
          memory = var.frontend_memory
        }
      }
    }

    scaling {
      min_instance_count = var.frontend_min_instances
      max_instance_count = var.frontend_max_instances
    }
  }

  # Routes 100% of traffic to the latest revision.
  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  # Ignore changes to the image after the service is created
  # as it will be updated via GitHub Actions
  lifecycle {
    ignore_changes = [
      template[0].containers[0].image
    ]
  }
}

resource "google_cloud_run_v2_service_iam_member" "frontend_public_access" {
  depends_on = [google_cloud_run_v2_service.frontend]

  name     = google_cloud_run_v2_service.frontend.name
  location = google_cloud_run_v2_service.frontend.location
  project  = google_cloud_run_v2_service.frontend.project
  role     = "roles/run.invoker"
  member   = "allUsers"
}
