terraform {
  required_version = "1.13.5"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "7.10.0"
    }
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_default_region
  zone    = var.gcp_default_zone
}
