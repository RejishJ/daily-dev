"""Domain objects describing a repository's history."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Commit:
    """A single commit as recorded in Git history."""

    sha: str
    author_name: str
    author_email: str
    authored_at: datetime
    subject: str

    @property
    def short_sha(self) -> str:
        """The commit hash abbreviated for display."""
        return self.sha[:7]
