project_id              = "web-app-demo-dev"
region                  = "europe-west1"
backend_image           = "europe-west1-docker.pkg.dev/web-app-demo-dev/backend/backend:latest"
backend_service_name    = "backend"
backend_min_instances   = 0  # Allow scaling to zero to minimize costs in dev
backend_max_instances   = 5