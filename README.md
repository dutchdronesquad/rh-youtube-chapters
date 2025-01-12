# RotorHazard Plugin Template

This is a basic template repository for creating a plugin for the RotorHazard timing platform. It is intended to be used as a starting point for creating a new plugin.

## Features

- **Pre-commit checks**: to run checks and tests on each commit.
- **Python virtual environment**: uses [uv] to manage the python virtual environment and dependencies.
- **RHFest validation**: GitHub action to validate the plugin manifest file against the RHFest schema.
- **Renovate**: uses [Renovate](https://docs.renovatebot.com/) to keep dependencies up to date.

## Development

How to setup the development environment.

### Prerequisites

You need the following tools to get started:

- [uv] - A python virtual environment/package manager
- [Python] 3.13 - The programming language

### Installation

1. Clone the repository
2. Install all dependencies with UV. This will create a virtual environment and install all dependencies

```bash
uv sync
```

3. Setup the pre-commit check, you must run this inside the virtual environment

```bash
uv run pre-commit install
```

### Run pre-commit checks

As this repository uses the [pre-commit][pre-commit] framework, all changes
are linted and tested with each commit. You can run all checks and tests
manually, using the following command:

```bash
uv run pre-commit run --all-files
```

To manual run only on the staged files, use the following command:

```bash
uv run pre-commit run
```

## License

Distributed under the **MIT** License. See [`LICENSE`](LICENSE) for more information.

<!-- LINK -->
[uv]: https://docs.astral.sh/uv/
[Python]: https://www.python.org/
[pre-commit]: https://pre-commit.com/
