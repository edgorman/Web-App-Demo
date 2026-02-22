project_id              = "web-app-demo-prod"
region                  = "europe-west1"
backend_service_name    = "backend"
backend_port            = 8080
backend_cpu             = "1"     # Minimum CPU required by Cloud Run V2
backend_memory          = "512Mi" # More memory for production workloads
backend_min_instances   = 0       # Allow scaling to zero to minimize costs
backend_max_instances   = 10

# Frontend service configuration
frontend_service_name  = "frontend"
frontend_port          = 8080
frontend_cpu           = "1"
frontend_memory        = "512Mi"
frontend_min_instances = 0 # Allow scaling to zero to minimize costs
frontend_max_instances = 10

# Google Identity Platform Configuration
# OAuth providers (client ID and secret injected from Secret Manager via GitHub Actions)
identity_platform_providers = {
  "google.com" = {
    enabled = true
  }
}
