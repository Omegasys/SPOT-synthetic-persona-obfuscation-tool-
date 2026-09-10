from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from threading import RLock
from typing import Callable, Iterable

from .events import AuditEvent, AuditSeverity


@dataclass
class AuditLogPolicy:
    """Controls local audit-log retention."""

    max_entries: int = 10_000
    minimum_severity: AuditSeverity = AuditSeverity.INFO

    def validate(self) -> None:
        """Validate audit-log policy."""
        if self.max_entries < 1:
            raise ValueError("max_entries must be positive.")


class AuditLog:
    """
    Thread-safe in-memory audit log.

    Persistent storage can be provided by the storage layer. This class
    intentionally does not perform filesystem or network operations.
    """

    _severity_order = {
        AuditSeverity.DEBUG: 0,
        AuditSeverity.INFO: 1,
        AuditSeverity.WARNING: 2,
        AuditSeverity.ERROR: 3,
        AuditSeverity.SECURITY: 4,
        AuditSeverity.EMERGENCY: 5,
    }

    def __init__(
        self,
        policy: AuditLogPolicy | None = None,
    ) -> None:
        self.policy = policy or AuditLogPolicy()
        self.policy.validate()

        self._events: deque[AuditEvent] = deque(
            maxlen=self.policy.max_entries
        )
        self._lock = RLock()

    def append(self, event: AuditEvent) -> bool:
        """Append an event if it meets the severity policy."""
        if not self._meets_severity(event.severity):
            return False

        with self._lock:
            self._events.append(event)

        return True

    def extend(
        self,
        events: Iterable[AuditEvent],
    ) -> int:
        """Append multiple events."""
        count = 0

        for event in events:
            if self.append(event):
                count += 1

        return count

    def all(self) -> list[AuditEvent]:
        """Return a snapshot of all retained events."""
        with self._lock:
            return list(self._events)

    def recent(self, limit: int = 100) -> list[AuditEvent]:
        """Return recent events."""
        if limit < 1:
            raise ValueError("limit must be positive.")

        with self._lock:
            return list(self._events)[-limit:]

    def filter(
        self,
        *,
        event_type: str | None = None,
        severity: AuditSeverity | None = None,
        persona_id: str | None = None,
    ) -> list[AuditEvent]:
        """Filter events without modifying the log."""
        with self._lock:
            events = list(self._events)

        if event_type is not None:
            events = [
                event
                for event in events
                if event.event_type == event_type
            ]

        if severity is not None:
            events = [
                event
                for event in events
                if event.severity == severity
            ]

        if persona_id is not None:
            events = [
                event
                for event in events
                if event.persona_id == persona_id
            ]

        return events

    def clear(self) -> None:
        """Clear retained audit events."""
        with self._lock:
            self._events.clear()

    def count(self) -> int:
        """Return the number of retained events."""
        with self._lock:
            return len(self._events)

    def subscribe(
        self,
        callback: Callable[[AuditEvent], None],
    ) -> Callable[[AuditEvent], None]:
        """
        Return a callback wrapper suitable for higher-level event systems.

        The audit log itself does not maintain external subscriptions.
        """
        if not callable(callback):
            raise TypeError("callback must be callable.")

        return callback

    def _meets_severity(
        self,
        severity: AuditSeverity,
    ) -> bool:
        return (
            self._severity_order[severity]
            >= self._severity_order[self.policy.minimum_severity]
        )
