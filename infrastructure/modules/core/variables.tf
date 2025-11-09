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

variable "gcp_services" {
  description = "The required GCP services to be enabled"
  type        = list(string)
  default     = ["iam.googleapis.com", "storage.googleapis.com"]
}

variable "terraform_state_admins" {
  description = "The set of developers with admin permissions to access the terraform state"
  type        = list(string)
  sensitive   = true
}

variable "github_access_token" {
  description = "The oauth token used to grant provider access to the GitHub repository"
  type        = string
  sensitive   = true
}

variable "github_repository_owner" {
  description = "The name of the owner of the GitHub repository"
  type        = string
  default     = "edgorman"
}

variable "github_repository_name" {
  description = "The name of the GitHub repository"
  type        = string
  default     = "Web-App-Demo"
}

variable "github_repository_admins" {
  description = "The set of developers with admin permissions to the github repository"
  type        = list(string)
  sensitive   = true
}

variable "github_repository_developers" {
  description = "The set of developers with developer permissions to the github repository"
  type        = list(string)
  default     = []
  sensitive   = true
}

variable "github_repository_viewers" {
  description = "The set of developers with developer permissions to the github repository"
  type        = list(string)
  default     = []
  sensitive   = true
}

variable "github_protected_branch" {
  description = "The GitHub branch that is protected by this terraform environment"
  type        = string
}

variable "github_protected_branch_require_admin_approval" {
  description = "Whether the GitHub protected branch requires admin approval"
  type        = bool
}
