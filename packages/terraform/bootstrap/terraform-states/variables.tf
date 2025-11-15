variable "gcp_project_id" {
  description = "The id of this GCP project"
  type        = string
  sensitive   = true
}

variable "remote_states" {
  description = "The remote Terraform states to configure and who has access to them"
  type        = list(
    object(
      {
        name_suffix = string
        admin_emails = list(string)
        location = optional(string, "EU")
        viewer_emails = optional(list(string), [])
      }
    )
  )
  sensitive = true
}

variable "remote_state_name_prefix" {
  description = "The text to prefix each remote state name with"
  type        = string
  default     = "web-app-demo"
}
