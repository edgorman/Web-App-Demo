# Grant the GitHub Actions service account necessary permissions on environment projects
# These permissions are required for Terraform to manage resources in dev/prod environments

# Grant Editor role to the GitHub Actions service account on each environment project
# This allows Terraform to create and manage most GCP resources
resource "google_project_iam_member" "github_actions_env_editor" {
  for_each = google_project.env_projects

  project = each.value.project_id
  role    = "roles/editor"
  member  = "serviceAccount:${google_service_account.github_actions.email}"
}

# Grant Cloud Run Admin role to the GitHub Actions service account on each environment project
# This is specifically required to manage IAM policies for Cloud Run services (e.g., public access)
resource "google_project_iam_member" "github_actions_env_run_admin" {
  for_each = google_project.env_projects

  project = each.value.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.github_actions.email}"
}
