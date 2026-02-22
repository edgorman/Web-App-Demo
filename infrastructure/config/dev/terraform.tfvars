project_id              = "web-app-demo-dev"
region                  = "europe-west1"
backend_service_name    = "backend"
backend_port            = 8080
backend_cpu             = "1"     # Minimum CPU required by Cloud Run V2
backend_memory          = "512Mi" # Minimum memory required by Cloud Run V2 with unthrottled CPU
backend_min_instances   = 0       # Allow scaling to zero to minimize costs in dev
backend_max_instances   = 5

# Frontend service configuration
frontend_service_name  = "frontend"
frontend_port          = 8080
frontend_cpu           = "1"
frontend_memory        = "512Mi"
frontend_min_instances = 0 # Allow scaling to zero to minimize costs
frontend_max_instances = 5

# Google Identity Platform / OAuth Configuration
# Get these from: https://console.cloud.google.com/apis/credentials
google_oauth_client_id     = "YOUR_CLIENT_ID.apps.googleusercontent.com"
google_oauth_client_secret = "YOUR_CLIENT_SECRET"

# Authorized domains for OAuth redirects
# Add your Cloud Run domain after deployment
identity_platform_authorized_domains = [
  "localhost"
]
