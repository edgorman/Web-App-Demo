project_id              = "web-app-demo-dev"
region                  = "europe-west1"
# Default placeholder image for initial infrastructure deployment (Google's public hello image).
# Replace with actual backend image after infrastructure is initialized:
# backend_image         = "europe-west1-docker.pkg.dev/web-app-demo-dev/backend/backend:latest"
backend_image           = "us-docker.pkg.dev/cloudrun/container/hello"
backend_service_name    = "backend"
backend_port            = 8080
backend_cpu             = "0.25"  # Minimum CPU for cost optimization
backend_memory          = "256Mi" # Minimum memory for cost optimization
backend_min_instances   = 0       # Allow scaling to zero to minimize costs in dev
backend_max_instances   = 5
