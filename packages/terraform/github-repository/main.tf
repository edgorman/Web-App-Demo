data "github_repository" "repository" {
  full_name = "${var.github_repository_owner}/${var.github_repository_name}"
}

resource "github_repository_collaborators" "users" {
  repository = data.github_repository.repository.name

  dynamic "user" {
    for_each = var.github_repository_admins
    iterator = github_username
    content {
      permission = "admin"
      username   = github_username.value
    }
  }

  dynamic "user" {
    for_each = var.github_repository_developers
    iterator = github_username
    content {
      permission = "push"
      username   = github_username.value
    }
  }

  dynamic "user" {
    for_each = var.github_repository_viewers
    iterator = github_username
    content {
      permission = "pull"
      username   = github_username.value
    }
  }
}

resource "github_branch_protection" "branch_protection" {
  repository_id = data.github_repository.repository.node_id
  pattern       = var.github_target_branch

  require_signed_commits          = true
  require_conversation_resolution = true

  required_pull_request_reviews {
    dismiss_stale_reviews           = true
    required_approving_review_count = 1
    require_code_owner_reviews      = var.github_target_branch_require_admin_approval
  }
}
