module "repository-branch" {
  source = "../../../packages/terraform/github/repository-branch"

  provider_token = var.github_provider_token
  target_branch  = var.github_target_branch
}
