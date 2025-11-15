variable "github_provider_token" {
  description = "The token used to grant provider access via the GitHub integration"
  type        = string
  sensitive   = true
}

variable "github_target_branch" {
  description = "The target branch in GitHub for this Terraform configuration"
  type        = string
}
