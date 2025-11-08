from collections.abc import Callable
from contextlib import nullcontext as no_exception
from typing import Optional
from unittest.mock import patch

import pytest

from config import GitHubGitHandlerConfig
from repository.github import new_github_git_handler


@pytest.mark.parametrize(
    "mock_error,expect_exception",
    [
        (None, no_exception()),
        (Exception("it exploded"), pytest.raises(Exception))
    ],
)
def test_new_github_git_handler(mock_error: Optional[Exception], expect_exception: Callable):
    with patch("repository.github.Repo", side_effect=mock_error):
        with expect_exception as e:
            new_github_git_handler(GitHubGitHandlerConfig())

        assert mock_error is None or e.value.__cause__ == mock_error
