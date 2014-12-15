"""Expected, user-facing error types.

Every error that is raised deliberately derives from
:class:`BackInTheDayError`, so the CLI can tell expected failures (shown as a
one-line message) apart from bugs (which keep their traceback).
"""

from __future__ import annotations


class BackInTheDayError(Exception):
    """Base class for errors that are safe to show to a user."""


class GitError(BackInTheDayError):
    """A git command could not be started or exited with a failure status."""

    def __init__(
        self,
        message: str,
        *,
        returncode: int | None = None,
        stderr: str = "",
    ) -> None:
        super().__init__(message)
        self.returncode = returncode
        self.stderr = stderr


class InvalidArgumentError(BackInTheDayError):
    """A value supplied by the caller or CLI user cannot be used."""
