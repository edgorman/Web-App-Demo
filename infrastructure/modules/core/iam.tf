resource "google_storage_bucket_iam_binding" "terraform_state_admin" {
  bucket = google_storage_bucket.terraform_state_bucket.name
  role   = "roles/storage.admin"

  members = [
    for user in var.terraform_state_admins : "user:${user}"
  ]
}
