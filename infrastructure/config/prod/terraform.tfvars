project_id              = "web-app-demo-prod"
region                  = "europe-west1"
# Default image - replace with actual backend image after infrastructure is initialized:
# backend_image         = "europe-west1-docker.pkg.dev/web-app-demo-prod/backend/backend:latest"
backend_image           = "us-docker.pkg.dev/cloudrun/container/hello"
backend_service_name    = "backend"
backend_port            = 8080  # Default hello image uses port 8080
backend_cpu             = "0.5"   # Slightly higher for production performance
backend_memory          = "512Mi" # More memory for production workloads
backend_min_instances   = 1       # Keep at least one instance warm to avoid cold starts
backend_max_instances   = 10
