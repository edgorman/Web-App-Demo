resource "github_repository" "repository" {
  name                   = var.name
  description            = var.description
  delete_branch_on_merge = true
}

resource "github_branch_default" "default_branch" {
  repository = github_repository.repository.name
  branch     = var.default_branch
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
