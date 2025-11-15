variable "gcp_root_project_id" {
  description = "The id of the root GCP project"
  type        = string
  sensitive   = true
}

variable "projects_base_name" {
  description = "The base name of the GCP projects to create/update"
  type        = string
  default     = "Web App Demo"
}

variable "projects_base_id" {
  description = "The base name of the GCP projects to create/update"
  type        = string
  sensitive   = true
}

variable "projects" {
  description = "The gcp projects to create/update"
  type        = list(
    object(
      {
        name_suffix = string
        id_suffix = string
      }
    )
  )
  default = []
}
