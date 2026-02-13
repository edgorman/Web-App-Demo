project_id              = "web-app-demo-prod"
region                  = "europe-west1"
backend_image           = "europe-west1-docker.pkg.dev/web-app-demo-prod/backend/backend:latest"
backend_service_name    = "backend"
backend_min_instances   = 1  # Keep at least one instance warm to avoid cold starts
backend_max_instances   = 10