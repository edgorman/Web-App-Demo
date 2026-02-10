variable "gcp_provider_project_id" {
  description = "The id of the root GCP project"
  type        = string
  default     = "web-app-demo-root"
}

variable "gcp_provider_region" {
  description = "The region of the root GCP project"
  type        = string
  default     = "europe-west1"
}

variable "gcp_provider_zone" {
  description = "The zone of the root GCP project"
  type        = string
  default     = "europe-west1-b"
}

variable "gcp_project_prefix" {
  description = "The prefix to use for all GCP projects"
  type        = string
  default     = "web-app-demo"
}

variable "gcp_projects" {
  description = "A list of GCP projects to create"
  type        = list(string)
  default     = ["dev", "prod"]
}

variable "github_provider_token" {
  description = "The token used to grant provider access to the GitHub repository"
  type        = string
  sensitive   = true
}

variable "github_repository_owner" {
  description = "The owner of the GitHub repository"
  type        = string
  default     = "edgorman"
}

variable "github_repository_name" {
  description = "The name of the GitHub repository"
  type        = string
  default     = "Web-App-Demo"
}

variable "github_default_branch" {
  description = "The default branch of the GitHub repository"
  type        = string
  default     = "main"
}

variable "github_env_branches" {
  description = "A list of GitHub branches used in environments"
  type        = list(string)
  default     = ["main", "develop"]
}