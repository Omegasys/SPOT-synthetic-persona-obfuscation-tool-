"""SPOT runtime state."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class SystemState:
    """Current state of the SPOT runtime."""

    running: bool = False
    emergency_stop: bool = False

    active_personas: Dict[str, str] = field(default_factory=dict)
    active_sessions: Dict[str, str] = field(default_factory=dict)
    active_tasks: Dict[str, str] = field(default_factory=dict)

    network_available: bool = False
    scheduler_enabled: bool = False

    def reset_runtime_state(self) -> None:
        """Clear transient runtime state."""
        self.running = False
        self.active_personas.clear()
        self.active_sessions.clear()
        self.active_tasks.clear()
