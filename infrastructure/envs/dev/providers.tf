terraform {
  required_version = "1.13.5"

  required_providers {
    github = {
      source  = "integrations/github"
      version = "6.7.5"
    }
  }

  backend "gcs" {
    bucket = ""
  }
}

provider "github" {
  token = var.github_provider_token
}
