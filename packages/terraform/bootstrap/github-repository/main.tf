locals {
  default_branch_name = tolist(
    [
      for branch in var.branches : branch.name
      if branch.default_branch == true
    ]
  )[0]
}

resource "github_repository" "repository" {
  name                   = var.repository_name
  description            = var.description
  delete_branch_on_merge = true
}

resource "github_branch_default" "default_branch" {
  repository = github_repository.repository.name
  branch     = local.default_branch_name
}

resource "github_branch_protection" "branches" {
  for_each      = { for branch in var.branches : branch.name => branch }
  repository_id = github_repository.repository.name
  pattern       = each.key

  require_signed_commits          = true
  require_conversation_resolution = true
  allows_deletions                = false
  allows_force_pushes             = false
  force_push_bypassers            = [ for user in var.admin_usernames : "/${user}" ]

  required_status_checks {
    strict = true
  }

  required_pull_request_reviews {
    dismiss_stale_reviews           = true
    required_approving_review_count = each.value.review_count
    require_code_owner_reviews      = each.value.code_owner_approval
  }
}

resource "github_repository_collaborators" "developers" {
  repository = github_repository.repository.name

  dynamic "user" {
    for_each = var.admin_usernames
    iterator = github_username
    content {
      permission = "admin"
      username   = github_username.value
    }
  }

  dynamic "user" {
    for_each = var.developer_usernames
    iterator = github_username
    content {
      permission = "push"
      username   = github_username.value
    }
  }

  dynamic "user" {
    for_each = var.viewer_usernames
    iterator = github_username
    content {
      permission = "pull"
      username   = github_username.value
    }
  }
}
