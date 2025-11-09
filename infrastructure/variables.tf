variable "gcp_project_id" {
  description = "The id of this GCP project"
  type        = string
  sensitive   = true
}

variable "gcp_default_region" {
  description = "The region of this GCP project"
  type        = string
  sensitive   = true
}

variable "gcp_default_zone" {
  description = "The zone of this GCP project"
  type        = string
  sensitive   = true
}

variable "environment" {
  description = "The environment of this configuration"
  type        = string
}

variable "developers" {
  description = "The set of developers with permissions across the project"
  type = map(
    object(
      {
        terraform_role  = string
        github_username = string
        github_role     = string
      }
    )
  )
  sensitive = true
}

variable "github_access_token" {
  description = "The access token used to grant provider access to the GitHub repository"
  type        = string
  sensitive   = true
}

variable "github_protected_branch" {
  description = "The GitHub branch that is protected by this terraform environment"
  type        = string
}
