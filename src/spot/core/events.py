"""SPOT event system."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List


@dataclass
class Event:
    """Represents an event occurring inside SPOT."""

    name: str
    source: str
    data: Dict[str, Any] = field(default_factory=dict)

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


EventHandler = Callable[[Event], None]


class EventBus:
    """Simple in-process event bus."""

    def __init__(self) -> None:
        self._handlers: Dict[str, List[EventHandler]] = {}

    def subscribe(
        self,
        event_name: str,
        handler: EventHandler,
    ) -> None:
        """Subscribe a handler to an event."""
        self._handlers.setdefault(event_name, []).append(handler)

    def unsubscribe(
        self,
        event_name: str,
        handler: EventHandler,
    ) -> None:
        """Remove a handler from an event."""
        handlers = self._handlers.get(event_name, [])

        if handler in handlers:
            handlers.remove(handler)

    def emit(self, event: Event) -> None:
        """Send an event to registered handlers."""
        handlers = self._handlers.get(event.name, [])

        for handler in list(handlers):
            handler(event)

        # '*' receives every event.
        for handler in list(self._handlers.get("*", [])):
            handler(event)
