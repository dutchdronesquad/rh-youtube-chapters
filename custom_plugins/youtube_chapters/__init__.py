"""YouTube Chapters plugin for RotorHazard."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from eventmanager import Evt
from flask import Blueprint, send_from_directory
from RHUI import UIField, UIFieldType

if TYPE_CHECKING:
    from Database import Heat


class YouTubeChapters:
    """YouTube Chapters plugin class."""

    BASE_DIR = Path(__file__).parent
    EXPORT_DIR = BASE_DIR / "data"
    LOG_FILE = EXPORT_DIR / "chapterslog.json"
    PREFIX = "YT Chapters"

    def __init__(self, rhapi: object) -> None:
        """Initialize YouTube Chapters.

        Args:
        ----
            rhapi (object): RotorHazard API object.

        """
        self.logger = logging.getLogger(__name__)
        self._rhapi = rhapi
        self.start_time = None
        self.chapters = []

        # Register UI elements
        self._register_ui()

        # Create a data directory if it doesn't exist
        Path(self.EXPORT_DIR).mkdir(parents=True, exist_ok=True)

    def _register_ui(self) -> None:
        """Register UI elements."""
        # UI Panel
        self._rhapi.ui.register_panel(
            name="youtube_chapters",
            label="YouTube Chapters",
            page="format",
        )
        self._rhapi.ui.register_panel(
            name="youtube_chapters_exports",
            label="Exported Chapters List",
            page="format",
        )
        self._rhapi.fields.register_option(
            field=UIField(
                name="start_time",
                label="Start Time of Livestream",
                field_type=UIFieldType.TEXT,
                desc="Fill in the format: YYYY-MM-DDTHH:MM:SS",
                placeholder="YYYY-MM-DDTHH:MM:SS",
            ),
            panel="youtube_chapters",
        )

        # Quickbuttons
        self._rhapi.ui.register_quickbutton(
            panel="youtube_chapters",
            name="set_start_time",
            label="Set Start Time",
            function=self.set_start_time,
        )
        self._rhapi.ui.register_quickbutton(
            panel="youtube_chapters",
            name="reset_chapters",
            label="Reset Chapter Log",
            function=self.reset_logger,
        )
        self._rhapi.ui.register_quickbutton(
            panel="youtube_chapters",
            name="export_chapters",
            label="Export Chapters",
            function=self.export_chapters,
        )

    def save_chapters(self) -> None:
        """Save chapters to a file."""
        data = {
            "start_time": self.start_time.strftime("%Y-%m-%d %H:%M:%S")
            if self.start_time
            else None,
            "chapters": [
                (ts.strftime("%Y-%m-%d %H:%M:%S"), heat) for ts, heat in self.chapters
            ],
        }
        with self.LOG_FILE.open("w") as file:
            json.dump(data, file)

        self.logger.info(f"{self.PREFIX}: chapters saved successfully.")

    def load_chapters(self, args: dict[str, str]) -> None:  # noqa: ARG002
        """Load chapters from a file."""
        if self.LOG_FILE.exists():
            with self.LOG_FILE.open() as file:
                try:
                    data = json.load(file)
                    self.start_time = (
                        datetime.strptime(
                            data["start_time"], "%Y-%m-%d %H:%M:%S"
                        ).replace(tzinfo=timezone.utc)
                        if data["start_time"]
                        else None
                    )
                    local_time = self.start_time.astimezone()
                    self._rhapi.db.option_set(
                        "start_time", local_time.strftime("%Y-%m-%dT%H:%M:%S")
                    )
                    self.chapters = [
                        (
                            datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").astimezone(
                                timezone.utc
                            ),
                            heat,
                        )
                        for ts, heat in data["chapters"]
                    ]

                    # Log the loaded data
                    if self.start_time:
                        self.logger.info(
                            f"{self.PREFIX}: loaded start time "
                            f"{self.start_time.strftime('%Y-%m-%d %H:%M:%S')} UTC"
                        )
                    if self.chapters:
                        self.logger.info(
                            f"{self.PREFIX}: loaded {len(self.chapters)} "
                            "saved chapters from previous session."
                        )
                except json.JSONDecodeError:
                    self.logger.exception(
                        "Failed to load chapter log file: invalid JSON format."
                    )
        else:
            self.logger.info(f"{self.PREFIX}: no log file found")
        self.update_exports_list()

    def set_start_time(self, args: dict[str, str]) -> None:  # noqa: ARG002
        """Set the start time for the stream."""
        start_time_str = self._rhapi.db.option("start_time")
        if not start_time_str:
            self._rhapi.ui.message_notify("No start time set.")
            return

        # Set the start time in UTC
        try:
            self.start_time = datetime.strptime(
                start_time_str, "%Y-%m-%dT%H:%M:%S"
            ).astimezone(timezone.utc)
            self._rhapi.ui.message_notify(
                f"Start time set to {self.start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}"
            )
            self.save_chapters()
        except ValueError:
            self._rhapi.db.option_set("start_time", "")
            self.start_time = None
            self._rhapi.ui.message_notify("Invalid date/time format.")

    def on_race_start(self, args: dict[str, str]) -> None:
        """Log a chapter entry at race start."""
        heat_info: Heat = self._rhapi.db.heat_by_id(args.get("heat_id"))
        round_number = self._rhapi.db.heat_max_round(args.get("heat_id"))

        # If heat_info.display_name is None, use "Practice" without round number
        if heat_info.display_name is None:
            heat_name = "Practice"
        else:
            # Always include the round number if a heat name is available
            heat_name = f"{heat_info.display_name} (Round {round_number + 1})"

        # Log the chapter
        current_time = datetime.now(timezone.utc)
        self.chapters.append((current_time, heat_name))
        self.logger.info(
            f"{self.PREFIX}: logged '{heat_name}' "
            f"at {current_time.strftime('%H:%M:%S')} UTC"
        )
        self.save_chapters()

    def reset_logger(self, args: dict[str, str]) -> None:  # noqa: ARG002
        """Reset clear chapters and remove log file."""
        self.start_time = None
        self.chapters = []

        # Remove the export files
        for txt_file in self.EXPORT_DIR.glob("*-youtube_chapters.txt"):
            txt_file.unlink()
            self.logger.info(f"{self.PREFIX}: Deleted file {txt_file.name}")

        # Remove the chapter log file
        if self.LOG_FILE.exists():
            self.LOG_FILE.unlink()
            self.logger.info(f"{self.PREFIX}: removing existing data file")

        # Clear the start time field
        self._rhapi.db.option_set("start_time", "")
        self.logger.info(f"{self.PREFIX}: All data cleared.")
        self._rhapi.ui.message_notify(
            "All chapters, export files, and the chapter log have been cleared."
        )
        self.update_exports_list()

    def export_chapters(self, args: dict[str, str]) -> None:  # noqa: ARG002
        """Export chapters with relative times."""
        # Check if there are chapters to export
        if not self.chapters:
            self._rhapi.ui.message_notify("No chapters to export.")
            return
        # Check if the start time is set
        if not self.start_time:
            self._rhapi.ui.message_notify(
                "No start time set. Please set a start time before exporting."
            )
            return

        # Filter chapters after the start time
        filtered_chapters = [
            (ts, heat_name) for ts, heat_name in self.chapters if ts >= self.start_time
        ]
        if not filtered_chapters:
            local_time = self.start_time.astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
            utc_time = self.start_time.strftime("%Y-%m-%d %H:%M:%S")
            self._rhapi.ui.message_notify(f"No chapters to export after {local_time}")
            self.logger.info(
                f"{self.PREFIX}: no chapters to export after {utc_time} UTC"
            )
            return

        # Add a timestamp to the filename
        timestamp = datetime.now().astimezone().strftime("%Y%m%d_%H%M%S")
        export_file = self.EXPORT_DIR / f"{timestamp}-youtube_chapters.txt"

        with export_file.open("w") as file:
            # Write the header information
            local_now = datetime.now().astimezone()
            local_start_time = self.start_time.astimezone()
            file.write(f"Export: {local_now.strftime('%Y-%m-%d %H:%M:%S %Z')}\n")
            file.write(f"Start: {local_start_time.strftime('%Y-%m-%d %H:%M:%S %Z')}\n")
            file.write("=" * 40 + "\n")

            # Write the start of the livestream
            file.write("00:00 - Start of Livestream\n")

            # Write the chapters
            for ts, heat_name in self.chapters:
                delta = (ts - self.start_time).total_seconds()

                # Format the time as HH:MM or HH:MM:SS
                hours, remainder = divmod(delta, 3600)
                minutes, seconds = divmod(remainder, 60)
                if hours > 0:
                    formatted_time = (
                        f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
                    )
                else:
                    formatted_time = f"{int(minutes):02}:{int(seconds):02}"
                file.write(f"{formatted_time} - {heat_name}\n")

        self._rhapi.ui.message_notify(
            f"YouTube chapters exported to data/{export_file.name}"
        )
        self.logger.info(f"{self.PREFIX}: exported to {export_file}.")

        # Update the list of exported files
        self.update_exports_list()

    def update_exports_list(self) -> None:
        """Update the Markdown list of export files."""
        export_files = sorted(
            self.EXPORT_DIR.glob("*-youtube_chapters.txt"), reverse=True
        )
        markdown_content = (
            "### Available Exports\n\n"
            if export_files
            else "### No Exports Available\n\n"
        )
        for file in export_files:
            markdown_content += f"- [{file.name}](/data/{file.name})\n"
        self._rhapi.ui.register_markdown(
            panel="youtube_chapters_exports",
            name="exported_files",
            desc=markdown_content,
        )


def initialize(rhapi: object) -> None:
    """Initialize plugin.

    Args:
    ----
        rhapi (object): RotorHazard API object.

    """
    plugin = YouTubeChapters(rhapi)

    # Register event listeners
    rhapi.events.on(Evt.STARTUP, plugin.load_chapters)
    rhapi.events.on(Evt.RACE_STAGE, plugin.on_race_start)

    bp = Blueprint("chapter_files", __name__, static_folder="data")

    @bp.route("/data/<path:filename>")
    def download_file(filename: str) -> None:
        return send_from_directory(plugin.EXPORT_DIR, filename)

    rhapi.ui.blueprint_add(bp)
