"""Command-line interface for SPOT."""

from __future__ import annotations

import argparse
import sys
from typing import Optional, Sequence

from spot import VERSION
from spot.core.engine import Engine
from spot.ui.commands import CommandHandler


def build_parser() -> argparse.ArgumentParser:
    """Build the SPOT command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="spot",
        description="SPOT — Synthetic Persona Obfuscation Tool.",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        title="commands",
    )

    subparsers.add_parser(
        "status",
        help="Show current SPOT system status.",
    )

    subparsers.add_parser(
        "start",
        help="Start the SPOT engine.",
    )

    subparsers.add_parser(
        "stop",
        help="Stop the SPOT engine.",
    )

    subparsers.add_parser(
        "emergency-stop",
        help="Immediately place SPOT into emergency-stop state.",
    )

    subparsers.add_parser(
        "reset-emergency-stop",
        help="Reset the emergency-stop state.",
    )

    persona_parser = subparsers.add_parser(
        "personas",
        help="Manage synthetic personas.",
    )

    persona_subparsers = persona_parser.add_subparsers(
        dest="persona_command",
    )

    persona_subparsers.add_parser(
        "list",
        help="List configured personas.",
    )

    persona_subparsers.add_parser(
        "active",
        help="List active personas.",
    )

    persona_parser_add = persona_subparsers.add_parser(
        "enable",
        help="Enable a persona.",
    )
    persona_parser_add.add_argument(
        "persona_id",
        help="Persona ID.",
    )

    persona_parser_disable = persona_subparsers.add_parser(
        "disable",
        help="Disable a persona.",
    )
    persona_parser_disable.add_argument(
        "persona_id",
        help="Persona ID.",
    )

    subparsers.add_parser(
        "tui",
        help="Launch the terminal user interface.",
    )

    return parser


def run(
    argv: Optional[Sequence[str]] = None,
    engine: Optional[Engine] = None,
) -> int:
    """Run the SPOT command-line interface."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if engine is None:
        engine = Engine()

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "tui":
        from spot.ui.tui import TUI

        interface = TUI(engine)
        interface.run()
        return 0

    handler = CommandHandler(engine)

    try:
        return handler.execute(args)
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


def main() -> None:
    """CLI entry point."""
    raise SystemExit(run())


if __name__ == "__main__":
    main()
