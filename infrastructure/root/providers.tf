terraform {
  required_version = "1.13.5"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "7.18.0"
    }
    github = {
      source  = "integrations/github"
      version = "6.7.5"
    }
  }

  backend "gcs" {
    bucket = ""
  }
}

provider "google" {
  project = var.gcp_provider_project_id
  region  = var.gcp_provider_region
  zone    = var.gcp_provider_zone
}

provider "github" {
  token = var.github_provider_token
}
