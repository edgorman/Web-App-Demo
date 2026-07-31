resource "google_firestore_database" "database" {
  depends_on = [google_project_service.env_services]

  project     = var.project_id
  name        = "${var.project_id}-database"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"
}
