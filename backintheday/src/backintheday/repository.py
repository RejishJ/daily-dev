"""Repository access: reads history from git and turns it into domain objects."""

from __future__ import annotations

import os
from datetime import datetime

from .errors import GitError
from .git_client import GitClient
from .models import Commit

# One line per commit, fields separated by NUL bytes. NUL cannot appear in
# git's metadata fields, which makes the output unambiguous to parse.
_LOG_FORMAT = "%H%x00%an%x00%ae%x00%aI%x00%s"
_FIELD_SEPARATOR = "\x00"

# git exits with status 128 when HEAD points to a branch without commits.
_EMPTY_REPOSITORY_MARKER = "does not have any commits"


def parse_commits(output: str) -> list[Commit]:
    """Parse the output of ``git log --format=...`` into commits.

    Raises:
        GitError: if a line does not match the expected format or a date
            cannot be parsed.
    """
    commits: list[Commit] = []
    for line in output.split("\n"):
        if not line:
            continue
        fields = line.split(_FIELD_SEPARATOR, 4)
        if len(fields) != 5:
            raise GitError(f"unexpected git log output: {line[:80]!r}")
        sha, author_name, author_email, authored_at, subject = fields
        try:
            authored = datetime.fromisoformat(authored_at)
        except ValueError as exc:
            raise GitError(f"unexpected git log date: {authored_at!r}") from exc
        commits.append(
            Commit(
                sha=sha,
                author_name=author_name,
                author_email=author_email,
                authored_at=authored,
                subject=subject,
            )
        )
    return commits


class GitRepository:
    """Exposes the commit history of a working directory."""

    def __init__(self, path: str | os.PathLike[str]) -> None:
        self._client = GitClient(path)

    def commits(self, limit: int | None = None) -> list[Commit]:
        """Return commits reachable from the current HEAD, newest first.

        Args:
            limit: maximum number of commits to return; ``None`` means all.

        Raises:
            GitError: if git fails, the directory is not a repository, or
                git's output cannot be parsed. A repository without any
                commits yields an empty list rather than an error.
        """
        args = [
            "log",
            # Deterministic output regardless of the user's git config.
            "--no-color",
            "--no-decorate",
            "--no-show-signature",
            "--date=iso-strict",
            f"--format={_LOG_FORMAT}",
        ]
        if limit is not None:
            args.append(f"--max-count={limit}")
        try:
            output = self._client.run(*args)
        except GitError as exc:
            if exc.returncode == 128 and _EMPTY_REPOSITORY_MARKER in exc.stderr:
                return []
            raise
        return parse_commits(output)
