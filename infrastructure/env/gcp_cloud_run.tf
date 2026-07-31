resource "google_cloud_run_v2_service" "backend" {
  depends_on = [google_project_service.env_services]

  name     = var.backend_service_name
  location = var.region
  project  = var.project_id

  template {
    service_account = google_service_account.backend.email

    containers {
      image = var.backend_image

      env {
        name  = "SERVICE__FASTAPI__CORS__ALLOW_ORIGINS"
        value = jsonencode(google_cloud_run_v2_service.frontend.urls)
      }

      env {
        name  = "SERVICE__AUTH__GOOGLE__CLIENT_ID"
        value = var.google_client_id
      }

      env {
        name  = "SERVICE__STORAGE__FIRESTORE__PROJECT_ID"
        value = var.project_id
      }

      env {
        name  = "SERVICE__STORAGE__FIRESTORE__DATABASE"
        value = google_firestore_database.database.name
      }

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
  #
  # client/client_version are also ignored: the deploy step in
  # service-push-commit runs `gcloud run deploy` to roll out the new image,
  # which stamps these fields onto the service. Since they aren't set in
  # this config, Terraform would otherwise want to null them out on every
  # subsequent plan/apply even though nothing meaningful changed.
  lifecycle {
    ignore_changes = [
      template[0].containers[0].image,
      client,
      client_version,
    ]
  }
}

# Grant frontend service account permission to invoke the backend.
#
# NOTE: this does NOT cover the browser -> backend calls the frontend actually
# makes today. The frontend is a static SPA (nginx serves the built assets and
# does not proxy /api), so requests to the backend originate from the end user's
# browser as anonymous traffic, not from this service account. This binding only
# matters for genuine server-side, service-to-service calls.
resource "google_cloud_run_v2_service_iam_member" "backend_frontend_access" {
  depends_on = [google_cloud_run_v2_service.backend]

  name     = google_cloud_run_v2_service.backend.name
  location = google_cloud_run_v2_service.backend.location
  project  = google_cloud_run_v2_service.backend.project
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.frontend.email}"
}

# Grant public access to invoke the backend.
#
# REQUIRED — do not remove without also changing how the frontend reaches the
# backend. The frontend fetches the backend directly from the user's browser
# using the build-time VITE_BACKEND_URL, with no credentials attached. Without
# an `allUsers` invoker binding, Cloud Run rejects those requests with a 403 at
# the edge before FastAPI runs. That 403 carries no CORS headers, so the browser
# surfaces it as a CORS error rather than as an auth failure — which is exactly
# how this presents when the binding is missing.
#
# The backend is not left unprotected by this: the FastAPI CORS middleware is
# configured from Terraform (see SERVICE__FASTAPI__CORS__ALLOW_ORIGINS above)
# and restricts which origins browsers will let call it.
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
  #
  # client/client_version are also ignored: the deploy step in
  # service-push-commit runs `gcloud run deploy` to roll out the new image,
  # which stamps these fields onto the service. Since they aren't set in
  # this config, Terraform would otherwise want to null them out on every
  # subsequent plan/apply even though nothing meaningful changed.
  lifecycle {
    ignore_changes = [
      template[0].containers[0].image,
      client,
      client_version,
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
