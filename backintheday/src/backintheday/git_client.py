"""Thin wrapper around the ``git`` command-line tool."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from .errors import GitError

# Keep git's output — error messages in particular — in a fixed locale so
# callers can rely on it regardless of the user's environment.
_FIXED_ENV = {"LC_ALL": "C", "LANG": "C"}


class GitClient:
    """Runs git commands inside a working directory."""

    def __init__(self, path: str | os.PathLike[str], executable: str = "git") -> None:
        self._path = Path(path).expanduser()
        self._executable = executable

    def run(self, *args: str) -> str:
        """Run ``git`` with the given arguments and return its standard output.

        Raises:
            GitError: if git is not installed, cannot be started, or the
                command exits with a non-zero status. The exception message
                is git's own standard error output.
        """
        command = (self._executable, "--no-pager", "-C", str(self._path), *args)
        env = {**os.environ, **_FIXED_ENV}
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                env=env,
            )
        except OSError as exc:
            raise GitError(
                f"could not run git executable: {self._executable}"
            ) from exc
        if completed.returncode != 0:
            message = completed.stderr.strip() or (
                f"git exited with status {completed.returncode}"
            )
            raise GitError(
                message,
                returncode=completed.returncode,
                stderr=completed.stderr,
            )
        return completed.stdout
