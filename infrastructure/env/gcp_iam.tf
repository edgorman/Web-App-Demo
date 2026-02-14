resource "google_project_iam_member" "github_actions_admin" {
  project = var.project_id
  role    = "roles/editor"
  member  = "serviceAccount:${var.github_actions_service_account}"
}

resource "google_project_iam_member" "github_actions_run_admin" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${var.github_actions_service_account}"
}
