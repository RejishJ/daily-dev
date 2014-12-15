# 0002. Keep the runtime standard-library only

- Status: accepted
- Date: 2026-09-28

## Context

CLI frameworks (click, typer), terminal formatters (rich), and Git libraries
would all shorten the code, but each adds a dependency tree that both
maintainers and users must track. The command surface of this project is
still small and likely to change.

## Decision

The runtime uses only the Python standard library: `argparse` for the CLI,
`dataclasses` for the domain model, `subprocess` for git access. `pytest` is
the single (test-only) dependency.

## Consequences

- Installing the tool involves no dependency resolution beyond Python and
  git themselves.
- Terminal niceties (colors, rich tables) are not available for free; if the
  output grows beyond aligned plain text, that is the signal to revisit this
  decision.
- The public CLI shape is still settling; committing to a framework now
  would bake early design choices into the project.
