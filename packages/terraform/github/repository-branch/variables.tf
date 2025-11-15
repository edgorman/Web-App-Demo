variable "provider_token" {
  description = "The token used to grant provider access via the GitHub integration"
  type        = string
  sensitive   = true
}

variable "repository_name" {
  description = "The name of the GitHub repository"
  type        = string
  default     = "Web-App-Demo"
}

variable "target_branch" {
  description = "The target branch in GitHub for this Terraform configuration"
  type        = string
}

variable "target_branch_required_review_count" {
  description = "The number of reviews required on a pull request"
  type        = number
  default     = 1
}

variable "target_branch_require_admin_approval" {
  description = "Whether the target branch requires admin approval"
  type        = bool
  default     = true
}

variable "target_branch_force_push_bypassers" {
  description = "The list of GitHub users able to force push for this branch"
  type        = list(string)
  default     = [ ]
  sensitive   = true
}
