from typing import List, Tuple

from git import Repo
from semver import Version

from repository.git import GitEventType, GitHandler


class GitHubGitHandler(GitHandler):
    def __init__(self, repository: Repo) -> None:
        """Initialise a GitHubGitHandler class

        Args:
            repository: the GitPython repository object
        """
        self.__repository = repository

    def get_files_changed(self, start_commit: str, end_commit: str) -> List[str]:
        """Get a list of file by their absolute file path that have changed between two commits.

        Args:
            start_commit: the start commit to get changes from
            end_commit: the end commit to get changes until
        Returns:
           list of files that were changed between the commits
        """
        try:
            diff = self.__repository.commit(start_commit).diff(end_commit)
        except Exception as e:
            raise Exception("Could not get diff from start/end commit.") from e

        if len(diff) == 0:
            raise Exception("No diff could be generated for start/end commit.")

        files = set(sum([(d.a_path, d.b_path) for d in diff]))

        return files

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
