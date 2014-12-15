# Architecture

## Purpose

Back in the Day reads a Git repository's history and presents it at a higher
level than the raw plumbing allows. This document describes how the code is
organized today and the rules that keep it easy to extend.

## Layers

The package under `src/backintheday/` is organized as four layers, each in
its own module:

| Layer | Module(s) | Responsibility |
|---|---|---|
| Presentation | `cli.py` | Argument parsing, output formatting, exit codes |
| Application | `history.py` | Use cases: validate input, orchestrate repository access |
| Domain | `models.py`, `errors.py` | Data types (`Commit`) and expected error types |
| Git access | `repository.py`, `git_client.py` | Run `git`, parse its output into domain objects |

Dependency direction is strictly one-way:

```
cli.py  ──▶  history.py  ──▶  repository.py  ──▶  git_client.py
   │            │                  │                    │
   └────────────┴──────────────────┴────────────────────┴──▶  models.py / errors.py
```

Rules:

1. Inner layers never import outer layers. `repository.py` must not know
   about `cli.py`; `git_client.py` must not know about `repository.py`.
2. Everything except `git_client.py` is free of process/OS concerns; only
   `git_client.py` invokes a subprocess.
3. Every deliberately raised error derives from `BackInTheDayError`
   (`errors.py`).

## Data flow of `backintheday history`

1. `cli.main()` parses arguments and calls `history.list_commits()`.
2. `history.list_commits()` validates the requested limit and constructs a
   `GitRepository`.
3. `GitRepository.commits()` asks `GitClient` to run
   `git log --format=... --max-count=...`.
4. `GitClient.run()` returns stdout, or raises `GitError` carrying git's
   stderr when the command fails.
5. The raw output is parsed into `Commit` objects (`parse_commits`).
6. `cli.format_commits()` renders the result as a table.

## Error handling

- Expected failures (not a repository, bad limit, git missing) raise
  `BackInTheDayError` subclasses; the CLI prints `error: ...` to stderr and
  exits with status 1.
- Argument parsing failures use argparse's own behaviour (exit status 2).
- Anything else is a bug: the traceback is left untouched on purpose.
- `git_client.py` pins `LC_ALL`/`LANG` to `C` so git's error messages are
  stable and testable regardless of the user's locale.

## Adding a command

A future command such as `backintheday activity` should follow the same
shape, without restructuring existing code:

1. Add the git-level reading to `repository.py` (e.g. a method that returns
   what the command needs), keeping it as NUL-delimited `git log` output.
2. Add an application module (`activity.py`) that validates input and uses
   `GitRepository`.
3. Add a subparser in `cli.build_parser()` and an `elif` branch in
   `cli.main()`, plus a formatting function for its output.

Modules are deliberately flat rather than nested: with the current size of
the project, one module per layer keeps imports obvious. Split a layer into
a package only when a single module becomes hard to navigate.

## Deliberate non-goals for this version

To stay a small foundation, this version does not include: a configuration
system, plugins, databases, networking, a report/export format, or any
third-party runtime dependency (see
[docs/decisions/0001](decisions/0001-use-git-cli-for-repository-access.md)
and
[docs/decisions/0002](decisions/0002-keep-runtime-standard-library-only.md)).
