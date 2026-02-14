project_id              = "web-app-demo-prod"
region                  = "europe-west1"
# Default placeholder image for initial infrastructure deployment (Google's public hello image).
# Replace with actual backend image after infrastructure is initialized:
# backend_image         = "europe-west1-docker.pkg.dev/web-app-demo-prod/backend/backend:latest"
backend_image           = "us-docker.pkg.dev/cloudrun/container/hello"
backend_service_name    = "backend"
backend_port            = 8080
backend_cpu             = "1"     # Minimum CPU required by Cloud Run V2
backend_memory          = "512Mi" # More memory for production workloads
backend_min_instances   = 1       # Keep at least one instance warm to avoid cold starts
backend_max_instances   = 10
