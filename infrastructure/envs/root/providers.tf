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

  backend "gcs" {
    bucket = ""
  }
}

provider "google" {
  project = var.gcp_root_project_id
  region  = var.gcp_root_region
  zone    = var.gcp_root_zone
}

provider "github" {
  token = var.github_provider_token
}
