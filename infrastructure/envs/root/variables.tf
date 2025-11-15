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

variable "github_admin_usernames" {
  description = "The set of developers with admin permissions to the GitHub repository"
  type        = list(string)
  sensitive   = true
}

variable "github_branches" {
  description = "The branch in GitHub to configure with the Terraform configuration"
  type = list(
    object(
      {
        name                = string
        default_branch      = optional(bool, false)
        review_count        = optional(number, 1)
        code_owner_approval = optional(bool, true)
      }
    )
  )
  default = [
    {
      name           = "main"
      default_branch = true
    }
  ]
}

variable "terraform_remote_states" {
  description = "The remote Terraform states to configure and who has access to them"
  type = list(
    object(
      {
        name_suffix = string
        location    = optional(string, "EU")
      }
    )
  )
}

variable "terraform_admin_emails" {
  description = "The set of developers with admin permissions to the Terraform remote states"
  type        = list(string)
  sensitive   = true
}

variable "terraform_viewer_emails" {
  description = "The set of developers with viewer permissions to the Terraform remote states"
  type        = list(string)
  sensitive   = true
  default     = []
}
