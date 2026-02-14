# Enable Cloud Run and Artifact Registry APIs for the environment project
resource "google_project_service" "env_services" {
  for_each = toset([
    "run.googleapis.com",
    "artifactregistry.googleapis.com"
  ])

  project = var.project_id
  service = each.value

  disable_on_destroy = false
}
