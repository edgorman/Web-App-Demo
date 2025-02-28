from typing import List

from config.config import GitHubGitHandlerConfig
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

    def get_cicd_files(self, file_path: str, event_type: GitEventType) -> List[str]:
        """Get the parent cicd files for a given file path and cicd event.

        Args:
            file_path: the child file path to get cicd for
            event_type: the type of git event that we are filtering by
        Returns:
            list of files in the parent cicd folder
        """

    def get_previous_push(self, identifier: str) -> str:
        """Get the previous push commit for a given history identifier (e.g. SHA, HEAD).

        Args:
            identifier: the history identifier of the current commit
        Returns:
            the previous push commit
        """
        # git rev-parse HEAD~1 # example

    def get_previous_release(self, identifier: str) -> str:
        """Get the previous release for a given release version.

        Args:
            release: the release identifier of the current release
        Returns:
            the previous release
        """
