# Contributing

## Getting started

Requirements: Python 3.10+ and git on `PATH`.

```console
python -m pip install -e .
python -m pytest
```

The tests create their own temporary Git repositories with fixed authors and
dates; they never read or modify your own repositories.

## Making changes

- Keep the layer boundaries described in
  [docs/architecture.md](docs/architecture.md): presentation → application →
  repository → git access, with `models.py`/`errors.py` shared underneath.
  Inner layers must not import outer ones.
- Add or extend tests for any behavior you change or introduce. Tests should
  assert real outcomes (files, commits, output), not just that code runs.
- Keep the runtime standard-library only (see
  [docs/decisions/0002](docs/decisions/0002-keep-runtime-standard-library-only.md)).
  If you need a third-party dependency, open a discussion first.
- Record decisions that future contributors should know about as a short
  record in `docs/decisions/`, numbered and following the format of the
  existing ones. Do not write records for routine choices.

## Commit messages

Write short, imperative summaries of what changed and why.
