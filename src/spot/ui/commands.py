"""Command handlers for the SPOT CLI."""

from __future__ import annotations

from argparse import Namespace
from typing import Any

from spot.core.engine import Engine
from spot.ui.status import StatusCollector


class CommandHandler:
    """Handle commands issued through the SPOT CLI."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self.status = StatusCollector(engine)

    def execute(self, args: Namespace) -> int:
        """Dispatch a parsed CLI command."""
        command = getattr(args, "command", None)

        handlers = {
            "status": self.status_command,
            "start": self.start_command,
            "stop": self.stop_command,
            "emergency-stop": self.emergency_stop_command,
            "reset-emergency-stop": self.reset_emergency_stop_command,
            "personas": self.personas_command,
        }

        handler = handlers.get(command)

        if handler is None:
            return 1

        return handler(args)

    def start_command(self, args: Namespace) -> int:
        """Start the SPOT engine."""
        del args

        self.engine.start()
        print("SPOT engine started.")
        return 0

    def stop_command(self, args: Namespace) -> int:
        """Stop the SPOT engine."""
        del args

        self.engine.stop()
        print("SPOT engine stopped.")
        return 0

    def emergency_stop_command(self, args: Namespace) -> int:
        """Activate the SPOT emergency stop."""
        del args

        self.engine.emergency_stop()
        print("EMERGENCY STOP ACTIVE.")
        print("SPOT activity should remain disabled until reset.")
        return 0

    def reset_emergency_stop_command(self, args: Namespace) -> int:
        """Reset the emergency-stop state."""
        del args

        controller = getattr(self.engine, "controller", None)

        if controller is None:
            print("Unable to reset emergency stop: controller unavailable.")
            return 1

        controller.reset_emergency_stop()

        print("Emergency-stop state reset.")
        return 0

    def status_command(self, args: Namespace) -> int:
        """Display current system status."""
        del args

        status = self.status.collect()
        print(status.to_text())
        return 0

    def personas_command(self, args: Namespace) -> int:
        """Handle persona subcommands."""
        command = getattr(args, "persona_command", None)

        if command == "list":
            return self.list_personas()

        if command == "active":
            return self.list_active_personas()

        if command == "enable":
            return self.enable_persona(args.persona_id)

        if command == "disable":
            return self.disable_persona(args.persona_id)

        print("Usage: spot personas {list,active,enable,disable}")
        return 1

    def _get_persona_manager(self) -> Any:
        """Return the persona manager if available."""
        manager = getattr(self.engine, "personas", None)

        if manager is None:
            manager = getattr(self.engine, "persona_manager", None)

        return manager

    def list_personas(self) -> int:
        """List configured personas."""
        manager = self._get_persona_manager()

        if manager is None:
            print("Persona manager is not configured.")
            return 1

        personas = manager.all()

        if not personas:
            print("No personas configured.")
            return 0

        for persona in personas:
            state = "enabled" if persona.enabled else "disabled"
            print(f"{persona.id}\t{persona.name}\t{state}")

        return 0

    def list_active_personas(self) -> int:
        """List active personas."""
        manager = self._get_persona_manager()

        if manager is None:
            print("Persona manager is not configured.")
            return 1

        personas = manager.active()

        if not personas:
            print("No active personas.")
            return 0

        for persona in personas:
            print(f"{persona.id}\t{persona.name}")

        return 0

    def enable_persona(self, persona_id: str) -> int:
        """Enable a persona."""
        manager = self._get_persona_manager()

        if manager is None:
            print("Persona manager is not configured.")
            return 1

        try:
            persona = manager.require(persona_id)
            persona.enable()
        except Exception as exc:
            print(f"Unable to enable persona: {exc}")
            return 1

        print(f"Persona '{persona_id}' enabled.")
        return 0

    def disable_persona(self, persona_id: str) -> int:
        """Disable a persona."""
        manager = self._get_persona_manager()

        if manager is None:
            print("Persona manager is not configured.")
            return 1

        try:
            persona = manager.require(persona_id)
            persona.disable()
        except Exception as exc:
            print(f"Unable to disable persona: {exc}")
            return 1

        print(f"Persona '{persona_id}' disabled.")
        return 0
