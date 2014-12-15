# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

### Added

- `backintheday history` — lists commits on the current branch (id, date,
  author, subject), newest first, with an optional path and `--limit`.
- Layered core: Git access (`git_client.py`, `repository.py`), domain model
  (`models.py`), application use cases (`history.py`), CLI (`cli.py`).
- Test suite covering Git access, history parsing, use cases, and the CLI.
- Architecture documentation and initial decision records.
