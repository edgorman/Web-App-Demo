from config import GitHubGitHandlerConfig

from .__git import GitHubGitHandler


def new_github_git_handler(config: GitHubGitHandlerConfig) -> GitHubGitHandler:
    return GitHubGitHandler(config)
