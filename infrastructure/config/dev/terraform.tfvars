project_id              = "web-app-demo-dev"
region                  = "europe-west1"
backend_service_name    = "backend"
backend_port            = 8080
backend_cpu             = "1"     # Minimum CPU required by Cloud Run V2
backend_memory          = "512Mi" # Minimum memory required by Cloud Run V2 with unthrottled CPU
backend_min_instances   = 0       # Allow scaling to zero to minimize costs in dev
backend_max_instances   = 5
