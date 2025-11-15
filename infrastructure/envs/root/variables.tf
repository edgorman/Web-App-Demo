variable "gcp_root_project_id" {
  description = "The id of the root GCP project"
  type        = string
  sensitive   = true
}

variable "gcp_root_region" {
  description = "The region of the root GCP project"
  type        = string
  sensitive   = true
}

variable "gcp_root_zone" {
  description = "The zone of the root GCP project"
  type        = string
  sensitive   = true
}

variable "gcp_projects_base_id" {
  description = "The base name of the GCP projects to create/update"
  type        = string
  sensitive   = true
}

variable "gcp_projects" {
  description = "The gcp projects to create/update"
  type = list(
    object(
      {
        name_suffix = string
        id_suffix   = string
      }
    )
  )
  default = []
}

variable "github_provider_token" {
  description = "The token used to grant provider access to the GitHub repository"
  type        = string
  sensitive   = true
}

variable "github_repository_admin_usernames" {
  description = "The set of developers with admin permissions to the GitHub repository"
  type        = list(string)
  sensitive   = true
}

variable "terraform_remote_states" {
  description = "The remote Terraform states to configure and who has access to them"
  type = list(
    object(
      {
        name_suffix = string
        admin_emails = list(string)
        location = optional(string, "EU")
        viewers_emails = optional(list(string), [])
      }
    )
  )
  sensitive = true
}
