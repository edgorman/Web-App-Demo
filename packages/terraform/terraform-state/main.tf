resource "google_project_service" "services" {
  for_each = toset(var.gcp_services)
  project  = var.gcp_project_id
  service  = each.value
}

resource "google_storage_bucket" "terraform_state_bucket" {
  depends_on = [google_project_service.services]

  name                        = "${var.gcp_project_id}-terraform-state"
  location                    = "EU"
  force_destroy               = true
  public_access_prevention    = "enforced"
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }
}

resource "google_storage_bucket_iam_binding" "terraform_state_admin" {
  bucket = google_storage_bucket.terraform_state_bucket.name
  role   = "roles/storage.admin"

  members = [
    for user in var.terraform_state_admins : "user:${user}"
  ]
}
