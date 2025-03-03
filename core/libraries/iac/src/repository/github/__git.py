from typing import List, Tuple

from semver import Version

from config import GitHubGitHandlerConfig
from repository.git import GitEventType, GitHandler


class GitHubGitHandler(GitHandler):
    def __init__(self, config: GitHubGitHandlerConfig) -> None:
        """Initialise a GitHubGitFileHandler class

        Args:
            config: the config needed to initialise the handler
        """
        self.__access_token = config.ACCESS_TOKEN  # example

    def get_files_changed(self, start_commit: str, end_commit: str) -> List[str]:
        """Get a list of file by their absolute file path that have changed between two commits.

        Args:
            start_commit: the start commit to get changes from
            end_commit: the end commit to get changes until
        Returns:
           list of files that were changed between the commits
        """
        raise NotImplementedError("get_files_changed is not implemented")

    def get_cicd_files(self, file_path: str, event_type: GitEventType) -> List[str]:
        """Get the parent cicd files for a given file path and cicd event.

        Args:
            file_path: the child file path to get cicd for
            event_type: the type of git event that we are filtering by
        Returns:
            list of files in the parent cicd folder
        """
        raise NotImplementedError("get_cicd_files is not implemented")

    def get_pull_request_commits(self, number: int) -> Tuple[str, str]:
        """Get the start/end commit from pull-request event.

        Args:
            number: the number of the pull-request
        Returns:
            the start commit
            the end commit
        """
        raise NotImplementedError("get_pull_request_commits is not implemented")

    def get_previous_push_commit(self, commit: str, branch: str) -> str:
        """Get the start commit from push event.

        Args:
            commit: the latest commit that was pushed
            branch: the branch to get commits from
        Returns:
            the previous push commit
        """
        # git rev-parse HEAD~1 # example
        raise NotImplementedError("get_previous_push_commit is not implemented")

    def get_previous_release_commit(self, version: Version) -> str:
        """Get the previous commit from release event.

        Args:
            version: the version of the release
        Returns:
            the previous release
        """
        raise NotImplementedError("get_previous_release_commit is not implemented")
