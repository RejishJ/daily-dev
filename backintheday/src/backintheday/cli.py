"""Command-line interface: argument parsing and output formatting."""

from __future__ import annotations

import argparse
import errno
import os
import sys
from collections.abc import Sequence

from . import __version__
from .errors import BackInTheDayError
from .history import list_commits
from .models import Commit


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="backintheday",
        description="Explore how a Git repository evolved over time.",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    commands = parser.add_subparsers(dest="command", metavar="command")

    history = commands.add_parser(
        "history",
        help="list commits on the current branch",
    )
    history.add_argument(
        "path",
        nargs="?",
        default=".",
        help="repository to inspect (default: current directory)",
    )
    history.add_argument(
        "-n",
        "--limit",
        type=int,
        metavar="N",
        help="show at most N commits",
    )
    return parser


def format_commits(commits: Sequence[Commit]) -> str:
    """Render commits as an aligned table, newest first."""
    if not commits:
        return "No commits found."
    authors = [f"{commit.author_name} <{commit.author_email}>" for commit in commits]
    author_width = max(len("AUTHOR"), *(len(author) for author in authors))
    rows = [f"{'COMMIT':<7}  {'DATE':<16}  {'AUTHOR':<{author_width}}  SUBJECT"]
    for commit, author in zip(commits, authors, strict=True):
        date = commit.authored_at.strftime("%Y-%m-%d %H:%M")
        rows.append(
            f"{commit.short_sha:<7}  {date:<16}  "
            f"{author:<{author_width}}  {commit.subject}"
        )
    return "\n".join(rows)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    try:
        commits = list_commits(args.path, limit=args.limit)
    except BackInTheDayError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    try:
        print(format_commits(commits))
        # Flush while we can still handle a closed pipe; otherwise the failure
        # happens at interpreter shutdown as "Exception ignored" noise.
        sys.stdout.flush()
    except OSError as exc:
        # A reader exiting early (e.g. `backintheday history | head`) closes
        # the pipe: EPIPE on POSIX, EINVAL on Windows. Other write failures
        # (disk full, ...) are real errors and keep their traceback.
        if exc.errno not in (errno.EPIPE, errno.EINVAL):
            raise
        # Point stdout at devnull so the shutdown flush cannot fail again,
        # then exit quietly with a failure status.
        # https://docs.python.org/3/library/signal.html#note-on-sigpipe
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        os.close(devnull)
        return 1
    return 0
