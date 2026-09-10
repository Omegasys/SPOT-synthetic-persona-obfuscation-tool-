"""SPOT lifecycle management."""

from __future__ import annotations

from enum import Enum


class LifecycleState(str, Enum):
    """Common lifecycle states used by SPOT components."""

    CREATED = "created"
    CONFIGURED = "configured"
    ENABLED = "enabled"
    STARTING = "starting"
    ACTIVE = "active"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"
    DISABLED = "disabled"
    DELETED = "deleted"


class Lifecycle:
    """Track the lifecycle of a SPOT component."""

    def __init__(
        self,
        initial_state: LifecycleState = LifecycleState.CREATED,
    ) -> None:
        self._state = initial_state

    @property
    def state(self) -> LifecycleState:
        """Return the current lifecycle state."""
        return self._state

    def transition(self, state: LifecycleState) -> None:
        """Change the lifecycle state."""
        self._state = state

    def is_active(self) -> bool:
        """Return whether the component is active."""
        return self._state == LifecycleState.ACTIVE

    def is_stopped(self) -> bool:
        """Return whether the component is stopped."""
        return self._state == LifecycleState.STOPPED

    def is_failed(self) -> bool:
        """Return whether the component has failed."""
        return self._state == LifecycleState.FAILED

    def reset(self) -> None:
        """Return the component to the created state."""
        self._state = LifecycleState.CREATED
