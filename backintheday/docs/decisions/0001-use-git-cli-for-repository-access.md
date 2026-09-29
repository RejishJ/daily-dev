# 0001. Use the git CLI for repository access

- Status: accepted
- Date: 2026-09-28

## Context

The tool needs commit metadata (ids, authors, dates, subjects) from a local
repository. Options considered:

1. Shell out to the `git` CLI.
2. GitPython — a Python object API over git.
3. libgit2 bindings (pygit2) — a native library with its own packaging.

## Decision

Use the `git` CLI through `subprocess`, isolated in a single module
(`git_client.py`), with machine-readable output (`git log --format` using
NUL-separated fields).

## Consequences

- Zero runtime dependencies; anyone with git installed can run the tool.
- Parsing git's output is our responsibility. NUL field separators make the
  format unambiguous; `repository.py` fails loudly (`GitError`) if git's
  output is not what we expect rather than mis-parsing it.
- git's messages are made locale-independent by pinning `LC_ALL`/`LANG`,
  which keeps error handling predictable and testable.
- Only the git-access layer knows how history is read. Swapping or
  supplementing the mechanism later (e.g. libgit2) does not touch the domain
  model, use cases, or CLI.
- Requires a `git` executable on `PATH` at runtime, which is a reasonable
  assumption for a tool aimed at developers.
