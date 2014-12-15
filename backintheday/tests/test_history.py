from pathlib import Path

import pytest

from backintheday.errors import GitError, InvalidArgumentError
from backintheday.history import list_commits

from conftest import NEWEST_FIRST, SampleRepo


def test_returns_commits_newest_first(sample_repo: SampleRepo) -> None:
    commits = list_commits(sample_repo.path)
    assert [commit.subject for commit in commits] == [
        spec.subject for spec in NEWEST_FIRST
    ]


@pytest.mark.parametrize("limit", [0, -1])
def test_limit_must_be_positive(sample_repo: SampleRepo, limit: int) -> None:
    with pytest.raises(InvalidArgumentError, match="limit must be at least 1"):
        list_commits(sample_repo.path, limit=limit)


def test_invalid_limit_is_reported_before_running_git(tmp_path: Path) -> None:
    # Not a repository: the limit check must fail first.
    with pytest.raises(InvalidArgumentError):
        list_commits(tmp_path, limit=0)


def test_git_failure_propagates(tmp_path: Path) -> None:
    with pytest.raises(GitError, match="not a git repository"):
        list_commits(tmp_path)
