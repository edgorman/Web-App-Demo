# VPC 
resource "google_compute_network" "vpc" {
  name                    = "${var.gcp_project_name}-vpc"
  auto_create_subnetworks = "false"
}

# Subnet
resource "google_compute_subnetwork" "subnet" {
  name          = "${var.gcp_project_name}-subnet"
  region        = var.gcp_project_region
  network       = google_compute_network.vpc.name
  ip_cidr_range = "10.10.0.0/24"
}

# Cluster
resource "google_container_cluster" "cluster" {
  name     = "${var.gke_cluster.name_prefix}-${var.environment}"
  location = var.gcp_project_zone

  remove_default_node_pool = true
  initial_node_count       = 1

  network    = google_compute_network.vpc.name
  subnetwork = google_compute_subnetwork.subnet.name
}

# Cluster Nodes
resource "google_container_node_pool" "cluster_nodes" {
  name       = google_container_cluster.cluster.name
  location   = var.gcp_project_zone
  cluster    = google_container_cluster.cluster.name
  node_count = var.gke_cluster.node_count

  node_config {
    machine_type = var.gke_cluster.machine_type
    spot = var.gke_cluster.use_spot_vms

    oauth_scopes = []
    labels = {
        region = var.gcp_project_region
        zone = var.gcp_project_zone
        environment = var.environment
        spot = var.gke_cluster.use_spot_vms
    }
    tags = [
        "${var.gke_cluster.name_prefix}-${var.environment}",
        var.gcp_project_region,
        var.gcp_project_zone,
        var.environment
    ]
  }
}
