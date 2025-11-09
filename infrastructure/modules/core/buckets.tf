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
