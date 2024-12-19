variable "gcp_project_name" {
  description = "The name of the GCP project"
  type = string
}

variable "gcp_project_region" {
  description = "The default region of the GCP project"
  type = string
}

variable "gcp_project_zone" {
  description = "The default zone of the GCP project"
  type = string
}

variable "environment" {
  description = "The environment"
  type = string
}

variable "gke_cluster" {
    description = "The cluster where all kubernetes manifests are applied."
    type = object({
      name_prefix = string
      node_count = number
      machine_type = string
      use_spot_vms = bool
    })
    default = {
      name_prefix = "primary"
      node_count = 1
      machine_type = "e2-small"
      use_spot_vms = true
    }
}
