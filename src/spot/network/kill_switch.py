"""SPOT fail-closed network kill switch."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class KillSwitchState(str, Enum):
    """Kill-switch states."""

    DISABLED = "disabled"
    ARMED = "armed"
    ACTIVE = "active"


@dataclass
class KillSwitch:
    """Track the state of a fail-closed network boundary."""

    enabled: bool = True
    state: KillSwitchState = (
        KillSwitchState.DISABLED
    )

    reason: str = ""

    def arm(self) -> None:
        """Arm the kill switch."""
        if not self.enabled:
            return

        self.state = KillSwitchState.ARMED
        self.reason = "Network kill switch armed."

    def activate(
        self,
        reason: str = "Network safety boundary triggered.",
    ) -> None:
        """Activate the kill switch."""
        if not self.enabled:
            return

        self.state = KillSwitchState.ACTIVE
        self.reason = reason

    def deactivate(self) -> None:
        """Deactivate the kill switch."""
        if not self.enabled:
            self.state = KillSwitchState.DISABLED
            return

        self.state = KillSwitchState.ARMED
        self.reason = "Kill switch deactivated."

    def disable(self) -> None:
        """Disable the kill switch."""
        self.enabled = False
        self.state = KillSwitchState.DISABLED
        self.reason = "Kill switch disabled."

    def enable(self) -> None:
        """Enable and arm the kill switch."""
        self.enabled = True
        self.arm()

    def allows_network(self) -> bool:
        """Return whether network traffic may proceed."""
        return (
            self.enabled
            and self.state == KillSwitchState.ARMED
        )

    def is_active(self) -> bool:
        """Return whether the kill switch is active."""
        return (
            self.state
            == KillSwitchState.ACTIVE
        )
