"""Reusable SPOT system status collection."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict

from spot.core.engine import Engine


@dataclass
class SystemStatus:
    """Snapshot of the current SPOT system state."""

    engine_state: str = "stopped"
    emergency_state: str = "ready"
    active_personas: int = 0
    sessions: int = 0
    tasks: int = 0
    network_state: str = "unknown"
    scheduler_state: str = "disabled"
    safety_state: str = "unknown"
    resource_state: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        """Convert the status snapshot to a dictionary."""
        return asdict(self)

    def to_text(self) -> str:
        """Convert the status snapshot to human-readable text."""
        return "\n".join(
            [
                "SPOT Status",
                "-----------",
                f"Engine:          {self.engine_state}",
                f"Emergency stop:  {self.emergency_state}",
                f"Active personas: {self.active_personas}",
                f"Sessions:        {self.sessions}",
                f"Tasks:           {self.tasks}",
                f"Network:         {self.network_state}",
                f"Scheduler:       {self.scheduler_state}",
                f"Safety:          {self.safety_state}",
                f"Resources:       {self.resource_state}",
            ]
        )


class StatusCollector:
    """Collect status from the SPOT engine and available subsystems."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def collect(self) -> SystemStatus:
        """Build a current system status snapshot."""
        state = getattr(self.engine, "state", None)

        status = SystemStatus()

        if state is not None:
            status.engine_state = (
                "running"
                if getattr(state, "running", False)
                else "stopped"
            )

            status.emergency_state = (
                "ACTIVE"
                if getattr(state, "emergency_stop", False)
                else "ready"
            )

            status.active_personas = len(
                getattr(state, "active_personas", set())
            )

            status.sessions = len(
                getattr(state, "sessions", set())
            )

            status.tasks = len(
                getattr(state, "tasks", set())
            )

            status.network_state = (
                "available"
                if getattr(state, "network_available", False)
                else "unavailable"
            )

            status.scheduler_state = (
                "enabled"
                if getattr(state, "scheduler_enabled", False)
                else "disabled"
            )

        status.active_personas = self._active_persona_count(
            status.active_personas
        )

        status.network_state = self._network_state(
            status.network_state
        )

        status.scheduler_state = self._scheduler_state(
            status.scheduler_state
        )

        status.safety_state = self._safety_state()
        status.resource_state = self._resource_state()

        return status

    def _active_persona_count(self, fallback: int) -> int:
        """Determine active persona count from the persona manager."""
        manager = getattr(self.engine, "personas", None)

        if manager is None:
            manager = getattr(self.engine, "persona_manager", None)

        if manager is None:
            return fallback

        try:
            return manager.count(active_only=True)
        except (TypeError, AttributeError):
            try:
                return len(manager.active())
            except (AttributeError, TypeError):
                return fallback

    def _network_state(self, fallback: str) -> str:
        """Determine network state when a network manager is available."""
        manager = getattr(self.engine, "network", None)

        if manager is None:
            manager = getattr(self.engine, "network_manager", None)

        if manager is None:
            return fallback

        try:
            if manager.health():
                return "healthy"
        except (AttributeError, TypeError):
            pass

        try:
            if manager.can_connect():
                return "available"
            return "unavailable"
        except (AttributeError, TypeError):
            return fallback

    def _scheduler_state(self, fallback: str) -> str:
        """Determine scheduler state when available."""
        scheduler = getattr(self.engine, "scheduler", None)

        if scheduler is None:
            return fallback

        try:
            return "enabled" if scheduler.enabled else "disabled"
        except AttributeError:
            return fallback

    def _safety_state(self) -> str:
        """Determine safety subsystem state."""
        safety = getattr(self.engine, "safety", None)

        if safety is None:
            safety = getattr(self.engine, "safety_manager", None)

        if safety is None:
            return "not configured"

        try:
            if safety.enabled:
                return "enabled"
        except AttributeError:
            pass

        return "available"

    def _resource_state(self) -> str:
        """Determine resource-limit subsystem state."""
        resources = getattr(self.engine, "resources", None)

        if resources is None:
            resources = getattr(
                self.engine,
                "resource_limits",
                None,
            )

        if resources is None:
            return "not configured"

        try:
            if resources.enabled:
                return "enabled"
        except AttributeError:
            pass

        return "available"
