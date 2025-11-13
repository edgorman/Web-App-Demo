variable "github_provider_token" {
  description = "The token used to grant provider access to the GitHub repository"
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

variable "github_target_branch" {
  description = "The target branch for this terraform configuration"
  type        = string
}

variable "github_target_branch_require_admin_approval" {
  description = "Whether the target branch requires admin approval"
  type        = bool
}
