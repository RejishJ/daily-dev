"""Application use cases for exploring a repository's history."""

from __future__ import annotations

import os

from .errors import InvalidArgumentError
from .models import Commit
from .repository import GitRepository


def list_commits(path: str | os.PathLike[str], limit: int | None = None) -> list[Commit]:
    """Return the commit history of the repository at *path*, newest first.

    Args:
        path: a directory inside the repository to inspect.
        limit: maximum number of commits to return; ``None`` returns all.

    Raises:
        InvalidArgumentError: if *limit* is not a positive number.
        GitError: if the history cannot be read.
    """
    if limit is not None and limit < 1:
        raise InvalidArgumentError(f"limit must be at least 1 (got {limit})")
    return GitRepository(path).commits(limit=limit)
