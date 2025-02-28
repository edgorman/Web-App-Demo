from abc import ABC, abstractmethod
from enum import Enum
from typing import List

GIT_HEAD_IDENTIFIER = "HEAD"


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
    def get_previous_push(self, identifier: str) -> str:
        """Get the previous push commit for a given history identifier (e.g. SHA, HEAD)."""

    @abstractmethod
    def get_previous_release(self, identifier: str) -> str:
        """Get the previous release for a given release version."""


class GitHandler(GitFileHandler, GitHistoryHandler):
    """A collection of interfaces that a Git handler must implement"""
