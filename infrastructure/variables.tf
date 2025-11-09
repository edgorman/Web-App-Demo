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

variable "admin_developers" {
  description = "The set of developers with admin permissions across the project"
  type        = list(string)
}
