"""SPOT core controller."""

from __future__ import annotations

from typing import Dict, Optional

from .events import Event, EventBus
from .session import Session
from .state import SystemState
from .task import Task


class Controller:
    """Coordinates SPOT sessions and tasks."""

    def __init__(
        self,
        state: Optional[SystemState] = None,
        event_bus: Optional[EventBus] = None,
    ) -> None:
        self.state = state or SystemState()
        self.event_bus = event_bus or EventBus()

        self.sessions: Dict[str, Session] = {}
        self.tasks: Dict[str, Task] = {}

    def create_session(self, session: Session) -> Session:
        """Register a new session."""
        if session.session_id in self.sessions:
            raise ValueError(
                f"Session already exists: {session.session_id}"
            )

        self.sessions[session.session_id] = session

        self.event_bus.emit(
            Event(
                name="session.created",
                source="controller",
                data={"session_id": session.session_id},
            )
        )

        return session

    def create_task(self, task: Task) -> Task:
        """Register a new task."""
        if task.task_id in self.tasks:
            raise ValueError(
                f"Task already exists: {task.task_id}"
            )

        self.tasks[task.task_id] = task

        self.event_bus.emit(
            Event(
                name="task.created",
                source="controller",
                data={"task_id": task.task_id},
            )
        )

        return task

    def stop_all(self) -> None:
        """Stop all active sessions and tasks."""
        for session in self.sessions.values():
            session.stop()

        for task in self.tasks.values():
            task.cancel()

    def emergency_stop(self) -> None:
        """Emergency-stop all controlled activity."""
        self.state.emergency_stop = True
        self.stop_all()

        self.event_bus.emit(
            Event(
                name="controller.emergency_stop",
                source="controller",
            )
        )

    def reset_emergency_stop(self) -> None:
        """Clear the emergency-stop state."""
        self.state.emergency_stop = False

        self.event_bus.emit(
            Event(
                name="controller.emergency_reset",
                source="controller",
            )
        )
