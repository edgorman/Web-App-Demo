import {
  id = var.github_repository_name
  to = github_repository.repository
}

resource "github_repository" "repository" {
  name                   = var.github_repository_name
  description            = "A demo repository for a web app"
  delete_branch_on_merge = true

  # Must stay in sync with the `allowed_merge_methods` used by the branch
  # rulesets below ("merge" for main, "squash" for develop) - a merge method
  # allowed by a ruleset but disabled here causes the merge button to fail
  # with a GraphQL "invalid value" error on $mergeMethod.
  allow_merge_commit = true
  allow_squash_merge = true
  allow_rebase_merge = false
}

resource "github_branch" "env_branches" {
  depends_on = [github_repository.repository]
  for_each   = toset(var.github_env_branches)
  repository = github_repository.repository.name
  branch     = each.value
}

resource "github_branch_default" "default_branch" {
  depends_on = [github_branch.env_branches]
  repository = github_repository.repository.name
  branch     = var.github_default_branch
}

resource "github_repository_ruleset" "branch_rulesets" {
  for_each   = toset(var.github_env_branches)
  depends_on = [github_branch.env_branches]

  name        = "${each.value} ruleset"
  repository  = github_repository.repository.name
  enforcement = "active"
  target      = "branch"

  rules {
    creation                = true
    update                  = false
    deletion                = true
    required_signatures     = true
    non_fast_forward        = true
    required_linear_history = true

    pull_request {
      dismiss_stale_reviews_on_push     = true
      require_code_owner_review         = true
      require_last_push_approval        = true
      required_review_thread_resolution = true
      required_approving_review_count   = 2
      allowed_merge_methods             = each.value == var.github_default_branch ? ["merge"] : ["squash"]
    }

  }

  conditions {
    ref_name {
      include = ["refs/heads/${each.value}"]
      exclude = []
    }
  }

  # Actor id 5 corresponds to the admin role when type is repository role
  # see https://registry.terraform.io/providers/integrations/github/latest/docs/resources/repository_ruleset#RepositoryRole-1
  bypass_actors {
    actor_id    = "5"
    actor_type  = "RepositoryRole"
    bypass_mode = "pull_request"
  }
}

resource "github_actions_variable" "root_project_id" {
  repository    = github_repository.repository.name
  variable_name = "ROOT_PROJECT_ID"
  value         = var.gcp_provider_project_id
}

resource "github_actions_variable" "google_client_id" {
  repository    = github_repository.repository.name
  variable_name = "GOOGLE_CLIENT_ID"
  value         = var.google_client_id
}
