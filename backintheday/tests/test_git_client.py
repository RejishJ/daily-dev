from pathlib import Path

import pytest

from backintheday.errors import GitError
from backintheday.git_client import GitClient


def test_runs_git_and_returns_stdout(tmp_path: Path) -> None:
    output = GitClient(tmp_path).run("--version")
    assert output.startswith("git version")


def test_directory_without_repository_raises_git_error(tmp_path: Path) -> None:
    with pytest.raises(GitError, match="not a git repository"):
        GitClient(tmp_path).run("log")


def test_missing_directory_raises_git_error(tmp_path: Path) -> None:
    with pytest.raises(GitError, match="cannot change to"):
        GitClient(tmp_path / "does-not-exist").run("log")


def test_missing_git_executable_raises_git_error(tmp_path: Path) -> None:
    client = GitClient(tmp_path, executable="git-does-not-exist")
    with pytest.raises(GitError, match="could not run git executable"):
        client.run("log")
