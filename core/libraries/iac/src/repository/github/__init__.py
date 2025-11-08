import tempfile

from git import Repo

from config import GitHubGitHandlerConfig

from .__git import GitHubGitHandler


def new_github_git_handler(config: GitHubGitHandlerConfig) -> GitHubGitHandler:
    try:
        directory = tempfile.TemporaryDirectory()
        repository = Repo(config.GITHUB_REPOSITORY_URL, directory)
    except Exception as e:
        raise Exception("Could not initialize the GitHubGitHandler.") from e

    return GitHubGitHandler(repository)
