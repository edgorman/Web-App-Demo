resource "google_project_service" "services" {
  for_each = toset([ "iam.googleapis.com", "storage.googleapis.com" ])
  project  = var.gcp_project_id
  service  = each.value
}

resource "google_storage_bucket" "buckets" {
  depends_on = [google_project_service.services]

  for_each                    = { for state in var.remote_states : state.name_suffix => state }
  name                        = "${var.remote_state_name_prefix}-terraform-state-${each.key}"
  location                    = each.value.location
  force_destroy               = true
  public_access_prevention    = "enforced"
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }
}

resource "google_storage_bucket_iam_binding" "bucket_admins" {
  for_each = { for state in var.remote_states : state.name_suffix => state }
  bucket   = google_storage_bucket.buckets[each.key].name
  role     = "roles/storage.objectAdmin"
  members  = [ for user in var.admin_emails : "user:${user}" ]
}

resource "google_storage_bucket_iam_binding" "bucket_viewers" {
  for_each = { for state in var.remote_states : state.name_suffix => state }
  bucket   = google_storage_bucket.buckets[each.key].name
  role     = "roles/storage.objectViewer"
  members  = [ for user in var.viewer_emails : "user:${user}" ]
}
