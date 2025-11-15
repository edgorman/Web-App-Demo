variable "provider_token" {
  description = "The token used to grant provider access via the GitHub integration"
  type        = string
  sensitive   = true
}

variable "owner" {
  description = "The name of the owner of the GitHub repository"
  type        = string
  default     = "edgorman"
}

variable "name" {
  description = "The name of the GitHub repository"
  type        = string
  default     = "Web-App-Demo"
}

variable "description" {
  description = "The description of the GitHub repository"
  type        = string
  default     = "A demo for a cloud configured web app delpoyed on the google cloud platform."
}

variable "default_branch" {
  description = "The default branch of the GitHub repository"
  type        = string
  default     = "main"
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
