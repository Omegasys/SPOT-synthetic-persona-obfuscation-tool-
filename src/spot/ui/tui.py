"""Simple terminal user interface for SPOT."""

from __future__ import annotations

import shutil
import sys
from typing import Optional

from spot.core.engine import Engine
from spot.ui.dashboard import Dashboard


class TUI:
    """Lightweight interactive terminal interface.

    This implementation intentionally uses only the Python standard library.
    A richer curses-based interface can be added later without changing the
    underlying SPOT engine.
    """

    def __init__(
        self,
        engine: Engine,
        input_stream=None,
        output_stream=None,
    ) -> None:
        self.engine = engine
        self.input_stream = input_stream or sys.stdin
        self.output_stream = output_stream or sys.stdout
        self.dashboard = Dashboard(engine)
        self.running = False

    def run(self) -> None:
        """Start the interactive terminal interface."""
        self.running = True

        self._write(self.dashboard.render())
        self._write("")
        self._write("Type 'help' for available commands.")

        while self.running:
            try:
                command = input("> ").strip()
            except EOFError:
                break
            except KeyboardInterrupt:
                self._write("")
                break

            self.handle_command(command)

    def handle_command(self, command: str) -> bool:
        """Handle one TUI command.

        Returns False when the interface should exit.
        """
        command = command.strip().lower()

        if not command:
            return True

        if command in {"quit", "exit", "q"}:
            self.running = False
            self._write("Exiting SPOT TUI.")
            return False

        if command in {"help", "h", "?"}:
            self._write(self.help_text())
            return True

        if command in {"status", "s", "refresh", "r"}:
            self._write(self.dashboard.render())
            return True

        if command == "start":
            self.engine.start()
            self._write("SPOT engine started.")
            return True

        if command == "stop":
            self.engine.stop()
            self._write("SPOT engine stopped.")
            return True

        if command in {"emergency-stop", "emergency", "stop-now"}:
            self.engine.emergency_stop()
            self._write("EMERGENCY STOP ACTIVE.")
            return True

        if command in {"clear", "cls"}:
            self.clear_screen()
            return True

        self._write(f"Unknown command: {command}")
        return True

    def help_text(self) -> str:
        """Return available TUI commands."""
        return "\n".join(
            [
                "SPOT TUI commands:",
                "",
                "  status           Show current status",
                "  refresh          Refresh the dashboard",
                "  start            Start the SPOT engine",
                "  stop             Stop the SPOT engine",
                "  emergency-stop   Activate emergency stop",
                "  clear            Clear the terminal",
                "  help             Show this help",
                "  quit             Exit the TUI",
            ]
        )

    def clear_screen(self) -> None:
        """Clear the terminal using ANSI escape sequences."""
        self._write("\033[2J\033[H")

    def terminal_size(self) -> shutil.os.terminal_size:
        """Return the current terminal size."""
        return shutil.get_terminal_size()

    def _write(self, text: str) -> None:
        """Write text to the configured output stream."""
        self.output_stream.write(text)
        self.output_stream.write("\n")
        self.output_stream.flush()
