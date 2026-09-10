from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from time import time


class EmergencyStopState(str, Enum):
    """Global emergency-stop states."""

    READY = "ready"
    ACTIVE = "active"
    RESET_REQUIRED = "reset_required"


@dataclass
class EmergencyStopEvent:
    """Record of an emergency-stop transition."""

    timestamp: float
    reason: str
    state: EmergencyStopState


@dataclass
class EmergencyStop:
    """
    Central emergency-stop controller.

    The controller only manages state and safety decisions. It does not
    directly terminate operating-system processes or modify networking.
    Integration layers are responsible for carrying out the shutdown.
    """

    state: EmergencyStopState = EmergencyStopState.READY
    reason: str | None = None
    activated_at: float | None = None
    history_limit: int = 50
    history: list[EmergencyStopEvent] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.history_limit < 1:
            raise ValueError("history_limit must be positive.")

    @property
    def active(self) -> bool:
        """Return whether emergency stop is active."""
        return self.state in {
            EmergencyStopState.ACTIVE,
            EmergencyStopState.RESET_REQUIRED,
        }

    def activate(self, reason: str = "manual emergency stop") -> None:
        """Activate the emergency stop."""
        if not reason:
            reason = "unspecified emergency stop"

        now = time()

        self.state = EmergencyStopState.ACTIVE
        self.reason = reason
        self.activated_at = now

        self._record_event(
            EmergencyStopEvent(
                timestamp=now,
                reason=reason,
                state=self.state,
            )
        )

    def request_reset(self) -> bool:
        """
        Move from ACTIVE to RESET_REQUIRED.

        A separate explicit reset operation is still required before
        normal activity can resume.
        """
        if self.state != EmergencyStopState.ACTIVE:
            return False

        self.state = EmergencyStopState.RESET_REQUIRED

        self._record_event(
            EmergencyStopEvent(
                timestamp=time(),
                reason="reset requested",
                state=self.state,
            )
        )

        return True

    def reset(self) -> bool:
        """Explicitly clear the emergency stop."""
        if self.state == EmergencyStopState.READY:
            return True

        self.state = EmergencyStopState.READY
        self.reason = None
        self.activated_at = None

        self._record_event(
            EmergencyStopEvent(
                timestamp=time(),
                reason="emergency stop reset",
                state=self.state,
            )
        )

        return True

    def allows_activity(self) -> bool:
        """Return whether normal activity is currently permitted."""
        return self.state == EmergencyStopState.READY

    def require_clear(self) -> None:
        """Raise an error if emergency stop is active."""
        if not self.allows_activity():
            raise RuntimeError(
                "SPOT emergency stop is active; reset is required."
            )

    def _record_event(self, event: EmergencyStopEvent) -> None:
        self.history.append(event)

        if len(self.history) > self.history_limit:
            self.history = self.history[-self.history_limit :]

    def clear_history(self) -> None:
        """Clear emergency-stop history."""
        self.history.clear()

    def summary(self) -> dict[str, object]:
        """Return current emergency-stop state."""
        return {
            "state": self.state.value,
            "active": self.active,
            "allows_activity": self.allows_activity(),
            "reason": self.reason,
            "activated_at": self.activated_at,
            "history_entries": len(self.history),
        }
