"""SPOT session management."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List

from .events import Event, EventBus
from .task import Task


@dataclass
class Session:
    """Represents one controlled SPOT execution session."""

    session_id: str
    persona_id: str
    event_bus: EventBus = field(default_factory=EventBus)

    tasks: List[Task] = field(default_factory=list)

    started_at: datetime | None = None
    stopped_at: datetime | None = None
    active: bool = False

    def start(self) -> None:
        """Start the session."""
        if self.active:
            return

        self.started_at = datetime.now(timezone.utc)
        self.stopped_at = None
        self.active = True

        self.event_bus.emit(
            Event(
                name="session.started",
                source="session",
                data={
                    "session_id": self.session_id,
                    "persona_id": self.persona_id,
                },
            )
        )

    def add_task(self, task: Task) -> None:
        """Add a task to the session."""
        self.tasks.append(task)

    def stop(self) -> None:
        """Stop the session and its tasks."""
        for task in self.tasks:
            task.cancel()

        self.active = False
        self.stopped_at = datetime.now(timezone.utc)

        self.event_bus.emit(
            Event(
                name="session.stopped",
                source="session",
                data={
                    "session_id": self.session_id,
                    "persona_id": self.persona_id,
                },
            )
        )
