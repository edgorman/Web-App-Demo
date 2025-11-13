terraform {
  required_version = "1.13.5"

  required_providers {
    github = {
      source  = "integrations/github"
      version = "6.7.5"
    }
  }
}

provider "github" {
  token = var.github_provider_token
  owner = var.github_repository_owner
}
