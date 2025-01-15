<!-- PROJECT SHIELDS -->
![Project Stage][project-stage-shield]
![Project Maintenance][maintenance-shield]
[![License][license-shield]](LICENSE)

# YouTube Chapters

When you publish a video on YouTube, you have the option to add a [chapters list](https://support.google.com/youtube/answer/9884579) in the description, which divides the video timeline into chapters for easier navigation.

This RotorHazard plugin will help you to generate a chapters list based on the start time of each heat. Ideal for when you want to publish the VOD of your livestream afterwards and make it easier for viewers to navigate to a specific round / heat of the race.

## Functionality

![alt plugin overview](https://raw.githubusercontent.com/dutchdronesquad/rh-youtube-chapters/main/assets/plugin_overview.png)

- Every time a heat starts it will be logged as a chapter entry.
- Based on the start time, the plugin will generate a list of chapters for YouTube.
- Export a txt file where you can copy/paste the chapters into your YouTube video description.

## Installation

> [!NOTE]
> This plugin is still in development and only works with the development branch of RotorHazard.

- Bash install script

## Getting started

1. Note when you started live streaming (local time).
2. Do the race timing as you are used to, each heat start will be logged automatically.
3. When you are done, fill in the start time and confirm with the `Set Start Time` button.
4. Click on `Export Chapters` to generate a txt file with the chapters.
    - You will see the download link after page refresh under **Exported Chapters List**.
5. Don't forget to reset the logging every time you have a new event.

## Setting up development environment

This Python project relies on [uv] as its dependency manager,
providing comprehensive management and control over project dependencies.

You need the following tools to get started:

- [uv] - A python virtual environment/package manager
- [Python] 3.11 (or higher) - The programming language

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
[license-shield]: https://img.shields.io/github/license/dutchdronesquad/rh-youtube-chapters.svg
[maintenance-shield]: https://img.shields.io/maintenance/yes/2025.svg
[project-stage-shield]: https://img.shields.io/badge/project%20stage-experimental-yellow.svg

[uv]: https://docs.astral.sh/uv/
[Python]: https://www.python.org/
[pre-commit]: https://pre-commit.com/
