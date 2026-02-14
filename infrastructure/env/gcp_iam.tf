# Grant the GitHub Actions service account Editor role on this environment project
resource "google_project_iam_member" "github_actions_admin" {
  project = var.project_id
  role    = "roles/editor"
  member  = "serviceAccount:${var.github_actions_service_account}"
}

# Grant the GitHub Actions service account Cloud Run Admin role
# This is required to manage IAM policies for Cloud Run services, such as enabling public access
resource "google_project_iam_member" "github_actions_run_admin" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${var.github_actions_service_account}"
}
