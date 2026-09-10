"""SPOT terminal dashboard."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from spot.core.engine import Engine
from spot.ui.status import StatusCollector, SystemStatus


@dataclass
class Dashboard:
    """Render SPOT status information for a terminal."""

    engine: Engine

    def __post_init__(self) -> None:
        self.status = StatusCollector(self.engine)

    def collect(self) -> SystemStatus:
        """Collect current dashboard status."""
        return self.status.collect()

    def render(self) -> str:
        """Render the dashboard as plain terminal text."""
        status = self.collect()

        lines = [
            "SPOT — Synthetic Persona Obfuscation Tool",
            "=" * 46,
            "",
            f"Engine:          {status.engine_state}",
            f"Emergency stop:  {status.emergency_state}",
            f"Active personas: {status.active_personas}",
            f"Sessions:        {status.sessions}",
            f"Tasks:           {status.tasks}",
            f"Network:         {status.network_state}",
            f"Scheduler:       {status.scheduler_state}",
            "",
            "Safety:",
            f"  Safety system: {status.safety_state}",
            f"  Resource use:  {status.resource_state}",
            "",
        ]

        return "\n".join(lines)

    def compact(self) -> str:
        """Return a compact one-line dashboard."""
        status = self.collect()

        return (
            f"engine={status.engine_state} "
            f"emergency={status.emergency_state} "
            f"personas={status.active_personas} "
            f"sessions={status.sessions} "
            f"tasks={status.tasks} "
            f"network={status.network_state}"
        )

    def as_dict(self) -> Dict[str, object]:
        """Return dashboard data as a dictionary."""
        return self.collect().to_dict()
