terraform {
  required_version = "~> 1.13"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.10"
    }
  }
}

provider "google" {
  project = var.gcp_root_project_id
}
