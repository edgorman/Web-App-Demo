variable "project_id" {
  description = "The GCP project ID for this environment"
  type        = string
}

variable "region" {
  description = "The GCP region for resources"
  type        = string
  default     = "europe-west1"
}

variable "backend_image" {
  description = "The container image for the backend service"
  type        = string
}

variable "backend_service_name" {
  description = "The name of the backend Cloud Run service"
  type        = string
  default     = "backend"
}

variable "backend_min_instances" {
  description = "Minimum number of instances for the backend service (0 for cost savings, 1+ to avoid cold starts)"
  type        = number
  default     = 0
}

variable "backend_max_instances" {
  description = "Maximum number of instances for the backend service"
  type        = number
  default     = 10
}