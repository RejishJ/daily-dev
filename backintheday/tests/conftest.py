"""Fixtures and expectations for tests that run against real Git repositories."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pytest


@dataclass(frozen=True, slots=True)
class CommitSpec:
    """A commit that a fixture repository is expected to contain."""

    subject: str
    author_name: str
    author_email: str
    authored_at: datetime


# The history written into `sample_repo`, oldest commit first.
EXPECTED_COMMITS: tuple[CommitSpec, ...] = (
    CommitSpec(
        "Add initial readme",
        "Alice",
        "alice@example.com",
        datetime.fromisoformat("2014-03-01T10:00:00+00:00"),
    ),
    CommitSpec(
        "Implement parser",
        "Bob",
        "bob@example.com",
        datetime.fromisoformat("2014-07-15T09:30:00+00:00"),
    ),
    CommitSpec(
        "Fix off-by-one in parser",
        "Alice",
        "alice@example.com",
        datetime.fromisoformat("2015-01-05T18:45:00+00:00"),
    ),
)

NEWEST_FIRST: tuple[CommitSpec, ...] = tuple(reversed(EXPECTED_COMMITS))


@dataclass(frozen=True, slots=True)
class SampleRepo:
    """A repository built by the `sample_repo` fixture."""

    path: Path
    shas: tuple[str, ...]  # commit ids, newest first


def _isolated_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    env = {
        **os.environ,
        # Ignore the machine's git configuration so tests behave the same
        # everywhere (no inherited aliases, signing, hooks, or locale).
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_SYSTEM": os.devnull,
        "LC_ALL": "C",
        "LANG": "C",
    }
    env.update(extra or {})
    return env


def run_git(path: Path, *args: str, env: dict[str, str] | None = None) -> str:
    """Run git in *path* with an isolated configuration and return its stdout."""
    completed = subprocess.run(
        ["git", "-C", str(path), *args],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=True,
        env=_isolated_env(env),
    )
    return completed.stdout


@pytest.fixture
def empty_repo(tmp_path: Path) -> Path:
    path = tmp_path / "empty-repo"
    path.mkdir()
    run_git(path, "init", "-b", "main")
    return path


@pytest.fixture
def sample_repo(tmp_path: Path) -> SampleRepo:
    path = tmp_path / "sample-repo"
    path.mkdir()
    run_git(path, "init", "-b", "main")

    shas: list[str] = []
    for number, spec in enumerate(EXPECTED_COMMITS):
        (path / f"change-{number}.txt").write_text(spec.subject + "\n", encoding="utf-8")
        run_git(path, "add", ".")
        run_git(
            path,
            "commit",
            "-m",
            spec.subject,
            env={
                "GIT_AUTHOR_NAME": spec.author_name,
                "GIT_AUTHOR_EMAIL": spec.author_email,
                "GIT_AUTHOR_DATE": spec.authored_at.isoformat(),
                "GIT_COMMITTER_NAME": spec.author_name,
                "GIT_COMMITTER_EMAIL": spec.author_email,
                "GIT_COMMITTER_DATE": spec.authored_at.isoformat(),
            },
        )
        shas.append(run_git(path, "rev-parse", "HEAD").strip())

    return SampleRepo(path=path, shas=tuple(reversed(shas)))
