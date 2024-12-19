terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "6.13.0"
    }
  }
}

provider "google" {
  project = var.gcp_project_name
  region = var.gcp_project_region
  zone = var.gcp_project_zone
}
