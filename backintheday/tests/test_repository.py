from datetime import datetime
from pathlib import Path

import pytest

from backintheday.errors import GitError
from backintheday.repository import GitRepository, parse_commits

from conftest import EXPECTED_COMMITS, SampleRepo


def test_returns_full_history_newest_first(sample_repo: SampleRepo) -> None:
    commits = GitRepository(sample_repo.path).commits()
    actual = [
        (commit.sha, commit.author_name, commit.author_email,
         commit.authored_at, commit.subject)
        for commit in commits
    ]
    expected = [
        (sha, spec.author_name, spec.author_email, spec.authored_at, spec.subject)
        for sha, spec in zip(sample_repo.shas, reversed(EXPECTED_COMMITS))
    ]
    assert actual == expected


def test_limit_returns_newest_commits_only(sample_repo: SampleRepo) -> None:
    commits = GitRepository(sample_repo.path).commits(limit=2)
    assert [commit.subject for commit in commits] == [
        spec.subject for spec in reversed(EXPECTED_COMMITS[-2:])
    ]


def test_reads_history_from_subdirectory(sample_repo: SampleRepo) -> None:
    subdir = sample_repo.path / "src"
    subdir.mkdir()
    commits = GitRepository(subdir).commits()
    assert len(commits) == len(EXPECTED_COMMITS)
    assert commits[0].sha == sample_repo.shas[0]


def test_repository_without_commits_returns_empty_list(empty_repo: Path) -> None:
    assert GitRepository(empty_repo).commits() == []


def test_directory_without_repository_raises_git_error(tmp_path: Path) -> None:
    plain = tmp_path / "plain"
    plain.mkdir()
    with pytest.raises(GitError, match="not a git repository"):
        GitRepository(plain).commits()


def test_parse_commits_reads_every_field() -> None:
    line = (
        "a" * 40
        + "\x00Alice\x00alice@example.com\x002014-03-01T10:00:00+00:00\x00Add readme"
    )
    [commit] = parse_commits(line + "\n")
    assert commit.sha == "a" * 40
    assert commit.short_sha == "a" * 7
    assert commit.author_name == "Alice"
    assert commit.author_email == "alice@example.com"
    assert commit.authored_at == datetime.fromisoformat("2014-03-01T10:00:00+00:00")
    assert commit.subject == "Add readme"


def test_parse_commits_rejects_malformed_line() -> None:
    with pytest.raises(GitError, match="unexpected git log output"):
        parse_commits("only-one-field")


def test_parse_commits_rejects_unparseable_date() -> None:
    line = "a" * 40 + "\x00Alice\x00alice@example.com\x00not-a-date\x00Add readme"
    with pytest.raises(GitError, match="unexpected git log date"):
        parse_commits(line)
