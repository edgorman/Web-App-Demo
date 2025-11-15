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

variable "description" {
  description = "The description of the GitHub repository"
  type        = string
  default     = "A demo for a cloud configured web app delpoyed on the google cloud platform."
}

variable "admin_usernames" {
  description = "The set of developers with admin permissions to the GitHub repository"
  type        = list(string)
  sensitive   = true
}

variable "developer_usernames" {
  description = "The set of developers with regular permissions to the GitHub repository"
  type        = list(string)
  default     = []
  sensitive   = true
}

variable "viewer_usernames" {
  description = "The set of developers with view-only permissions to the GitHub repository"
  type        = list(string)
  default     = []
  sensitive   = true
}

variable "branches" {
  description = "The branch in GitHub to configure with the Terraform configuration"
  type        = list(
    object(
      {
        name = string
        default_branch = optional(bool, false)
        review_count = optional(number, 1)
        code_owner_approval = optional(bool, true)
      }
    )
  )
}
