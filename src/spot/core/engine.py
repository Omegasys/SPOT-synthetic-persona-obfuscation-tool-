"""SPOT core execution engine."""

from __future__ import annotations

from typing import Optional

from .controller import Controller
from .events import EventBus, Event
from .state import SystemState


class Engine:
    """Main runtime engine for SPOT."""

    def __init__(
        self,
        controller: Optional[Controller] = None,
        event_bus: Optional[EventBus] = None,
    ) -> None:
        self.event_bus = event_bus or EventBus()
        self.state = SystemState()
        self.controller = controller or Controller(
            state=self.state,
            event_bus=self.event_bus,
        )

        self._running = False

    @property
    def running(self) -> bool:
        """Return whether the engine is currently running."""
        return self._running

    def start(self) -> None:
        """Start the SPOT engine."""
        if self._running:
            return

        self._running = True
        self.state.running = True

        self.event_bus.emit(
            Event(
                name="engine.started",
                source="engine",
            )
        )

    def stop(self) -> None:
        """Stop the SPOT engine."""
        if not self._running:
            return

        self.controller.stop_all()

        self._running = False
        self.state.running = False

        self.event_bus.emit(
            Event(
                name="engine.stopped",
                source="engine",
            )
        )

    def emergency_stop(self) -> None:
        """Immediately stop active SPOT work."""
        self.controller.emergency_stop()

        self._running = False
        self.state.running = False

        self.event_bus.emit(
            Event(
                name="engine.emergency_stop",
                source="engine",
            )
        )
