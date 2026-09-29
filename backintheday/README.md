# Back in the Day

Back in the Day is a command-line tool for exploring how a Git repository
evolved over time.

## The problem

`git log` answers "what happened recently". Harder questions — how activity
was distributed over the life of a project, how a file evolved, how two
periods of development differ — mean assembling plumbing commands by hand and
interpreting their output yourself. Back in the Day exists to turn Git's raw
history into higher-level views of a repository's past.

## What the current version does

The project is at its initial foundation stage. Today it does one thing:

```console
$ backintheday history
COMMIT   DATE                 AUTHOR                    SUBJECT
1a2b3c4  2014-06-01 12:00     Alice <alice@example.com> Add initial parser
...
```

`backintheday history` lists the commits on the current branch — id, date,
author, and subject — newest first. It accepts an optional path to another
repository and an optional `--limit N`:

```console
$ backintheday history path/to/repo --limit 20
```

Alongside the command, this version establishes the layered code structure
(see below) that future commands will be built on. It does **not** yet
analyse activity, compare periods, track files, or produce reports; those are
future work, described in [docs/architecture.md](docs/architecture.md).

## Requirements

- Python 3.10 or newer
- Git available on `PATH`

There are no third-party runtime dependencies.

## Development

```console
python -m pip install -e .    # optional: installs the `backintheday` command
python -m pytest              # run the test suite (works without installing)
backintheday history          # or: python -m backintheday history
```

Tests use only `pytest` and create their own temporary Git repositories, so
they run against a real `git` and never touch your project history.

## Architecture

The source is split into four layers with a one-way dependency direction:

- **Git access** (`git_client.py`, `repository.py`) — runs git and parses its
  output into domain objects.
- **Domain model** (`models.py`) — plain data types such as `Commit`.
- **Application** (`history.py`) — use cases that validate input and combine
  repository access.
- **Presentation** (`cli.py`) — argument parsing and output formatting.

The reasoning, the rules for adding new commands, and the decisions made so
far are documented in:

- [docs/architecture.md](docs/architecture.md)
- [docs/decisions/](docs/decisions/)

## Public interface

The command-line interface documented above is the supported, user-facing
API of this project, together with the package's `__version__` value.
Individual Python modules under `backintheday.*` are internal implementation
details and are not a stable public API unless they are explicitly
documented as public in a future release.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — see [LICENSE](LICENSE).
