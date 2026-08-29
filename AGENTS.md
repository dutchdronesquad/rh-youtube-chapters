# AGENTS.md

Guidance for AI/code agents working in this repository.

## Project Overview

`rh-youtube-chapters` is a RotorHazard Community Plugin that records race heat start times and exports a YouTube chapter list for livestream VOD descriptions.

The installable plugin lives under `custom_plugins/youtube_chapters/`. The repository root contains plugin metadata, development tooling, assets, and the install helper script.

## Repository Layout

- `custom_plugins/youtube_chapters/__init__.py`: complete RotorHazard plugin implementation, UI panels, event handlers, chapter persistence, export generation, and download route.
- `custom_plugins/youtube_chapters/manifest.json`: RotorHazard community plugin manifest. Keep plugin metadata and release version here.
- `tools/install.sh`: install helper script.
- `assets/plugin_overview.png`: README image asset.
- `README.md`: user-facing installation and usage documentation.
- `pyproject.toml`: project metadata, dependency groups, and Ruff configuration.
- `uv.lock`: locked Python development dependencies.

## Runtime Behavior

- On initialization, the plugin registers RotorHazard UI panels on the `format` page.
- The `start_time` UI field stores the livestream start time as a local datetime input.
- `Evt.STARTUP` loads saved chapter state from RotorHazard data storage.
- `Evt.RACE_STAGE` logs a chapter entry when a heat is staged.
- Chapter state is saved in `rh-data/youtube_chapters/chapterslog.json`.
- Exported YouTube chapter files are written to `rh-data/youtube_chapters/*-youtube_chapters.txt`.
- Exported files are exposed through the plugin blueprint under `/data/<filename>`.

## Development Environment

- Python: `>=3.11`
- Dependency manager: `uv`
- Lint/format hooks: `prek` plus `ruff`
- CI validation: RHFest via `ghcr.io/rotorhazard/rhfest-action:v3.0.1`

Set up dependencies from the repository root:

```bash
uv sync --all-groups
```

Install hooks when needed:

```bash
uv run prek install
```

## Common Commands

Run all configured checks:

```bash
uv run prek run --all-files
```

Run Ruff directly:

```bash
uv run ruff check .
uv run ruff format .
```

Run RHFest validation locally when Docker is available:

```bash
docker run --rm --pull=always -v .:/repo ghcr.io/rotorhazard/rhfest-action:latest
```

## Coding Conventions

- Follow the existing single-module plugin style unless a change clearly needs extraction.
- Keep RotorHazard imports such as `eventmanager`, `RHUI`, `Database`, and `rhapi` interactions inside runtime plugin code. They may not be importable outside a RotorHazard environment.
- Use timezone-aware datetimes. Internally, chapter timestamps and the stored livestream start time should be UTC; UI display/export may use local time.
- Preserve the exported YouTube chapter format: `00:00 - Start of Livestream`, followed by `MM:SS` or `HH:MM:SS` chapter offsets.
- Keep filesystem writes scoped to the plugin data directory under `rhapi.server.data_dir / "youtube_chapters"`.
- Be careful with `/data/<filename>` routes; do not broaden file serving beyond the export directory.
- Keep UI names and option keys stable unless a migration is included. Existing saved state depends on `start_time`, `chapterslog.json`, and the export filename pattern.
- The plugin currently has no standalone test suite. Prefer small, easily reviewable changes and run lint/format checks.

## Validation Checklist

Before handing off changes, run the narrowest relevant checks:

- Python/plugin change: `uv run ruff check .` and `uv run ruff format .`, or `uv run prek run --all-files`.
- Manifest/community-plugin change: run RHFest validation when Docker is available.
- README/install-script change: review commands manually and run formatting/lint checks where applicable.

If a command cannot run because local dependencies, Docker, network access, or RotorHazard runtime are unavailable, state that explicitly in the handoff.

## Git and Generated Files

- This repository may have uncommitted user changes. Do not revert unrelated changes.
- Keep `manifest.json` version aligned with intended plugin releases; `pyproject.toml` currently uses `0.0.0` as project metadata.
- Do not commit local RotorHazard data exports or generated chapter files.
