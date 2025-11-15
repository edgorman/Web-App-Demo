resource "github_branch_protection" "branch_protection" {
  repository_id = var.repository_name
  pattern       = var.target_branch

  require_signed_commits          = true
  require_conversation_resolution = true
  allows_deletions                = false
  allows_force_pushes             = false
  force_push_bypassers            = [ for user in var.target_branch_force_push_bypassers : "/${user}" ]

  required_status_checks {
    strict = true
  }

  required_pull_request_reviews {
    dismiss_stale_reviews           = true
    required_approving_review_count = var.target_branch_required_review_count
    require_code_owner_reviews      = var.target_branch_require_admin_approval
  }
}
