from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Tuple

from semver import Version


class GitEventType(Enum):
    PULL_REQUEST = 1
    PUSH = 2
    RELEASE = 3


class GitFileHandler(ABC):
    @abstractmethod
    def get_files_changed(self, start_commit: str, end_commit: str) -> List[str]:
        """Get a list of file by their absolute file path that have changed between two commits."""

    @abstractmethod
    def get_cicd_files(self, file_path: str, event_type: GitEventType) -> List[str]:
        """Get a list of cicd files for a given file path and cicd event."""


class GitHistoryHandler(ABC):
    @abstractmethod
    def get_pull_request_commits(self, number: int) -> Tuple[str, str]:
        """Get the start/end commit from pull-request event."""

    @abstractmethod
    def get_previous_push_commit(self, commit: str, branch: str) -> str:
        """Get the start commit from push event."""

    @abstractmethod
    def get_previous_release_commit(self, version: Version) -> str:
        """Get the previous commit from release event."""


class GitHandler(GitFileHandler, GitHistoryHandler):
    """A collection of interfaces that a Git handler must implement."""
