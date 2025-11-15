terraform {
  required_version = "~> 1.13"

  required_providers {
    github = {
      source  = "integrations/github"
      version = "~> 6.7"
    }
  }
}

provider "github" {
  token = var.provider_token
}
