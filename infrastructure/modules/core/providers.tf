terraform {
  required_version = "1.13.5"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "7.10.0"
    }

    github = {
      source  = "integrations/github"
      version = "6.7.5"
    }
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_default_region
  zone    = var.gcp_default_zone
}

provider "github" {
  token = var.github_access_token
  owner = var.github_repository_owner
}
