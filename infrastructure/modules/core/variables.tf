variable "gcp_project_id" {
  description = "The id of this GCP project"
  type        = string
}

variable "gcp_default_region" {
  description = "The region of this GCP project"
  type        = string
}

variable "gcp_default_zone" {
  description = "The zone of this GCP project"
  type        = string
}

variable "gcp_services" {
  description = "The required gcp services to be enabled"
  type        = list(string)
  default     = ["iam.googleapis.com", "storage.googleapis.com"]
}

variable "terraform_state_admins" {
  description = "The set of developers with admin permissions to access the terraform state"
  type        = list(string)
}
