resource "google_service_account" "github_actions" {
  project      = var.gcp_provider_project_id
  account_id   = "github-actions"
  display_name = "GitHub Actions Service Account"
}

resource "google_iam_workload_identity_pool" "github_pool" {
  project                   = var.gcp_provider_project_id
  workload_identity_pool_id = "github-pool"
  display_name              = "GitHub Pool"
}

resource "google_iam_workload_identity_pool_provider" "github_provider" {
  project                            = var.gcp_provider_project_id
  workload_identity_pool_id          = google_iam_workload_identity_pool.github_pool.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-provider"
  display_name                       = "GitHub Provider"

  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.repository" = "assertion.repository"
    "attribute.actor"      = "assertion.actor"
  }

  attribute_condition = "assertion.repository == '${var.github_repository_owner}/${var.github_repository_name}'"

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

resource "google_service_account_iam_member" "github_actions_wic" {
  service_account_id = google_service_account.github_actions.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github_pool.name}/attribute.repository/edgorman/${var.github_repository_name}"
}

resource "google_project_iam_member" "github_actions_admin" {
  project = var.gcp_provider_project_id
  role    = "roles/editor" # Or more specific roles as needed
  member  = "serviceAccount:${google_service_account.github_actions.email}"
}
