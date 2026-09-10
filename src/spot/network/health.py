"""SPOT network health monitoring."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List


class HealthState:
    """Network health states."""

    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"


@dataclass
class HealthCheck:
    """Result of a network health check."""

    name: str
    passed: bool
    message: str = ""

    checked_at: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )


@dataclass
class NetworkHealth:
    """Track network route health."""

    state: str = HealthState.UNKNOWN

    checks: List[HealthCheck] = field(
        default_factory=list
    )

    def add_check(
        self,
        check: HealthCheck,
    ) -> None:
        """Record a health check."""
        self.checks.append(check)
        self._recalculate()

    def clear(self) -> None:
        """Clear health-check history."""
        self.checks.clear()
        self.state = HealthState.UNKNOWN

    def healthy(self) -> bool:
        """Return whether the route is currently healthy."""
        return self.state == HealthState.HEALTHY

    def failed(self) -> bool:
        """Return whether the route has failed."""
        return self.state == HealthState.FAILED

    def latest(
        self,
        name: str,
    ) -> HealthCheck | None:
        """Return the latest check with a given name."""
        for check in reversed(self.checks):
            if check.name == name:
                return check

        return None

    def _recalculate(self) -> None:
        """Recalculate overall network health."""
        if not self.checks:
            self.state = HealthState.UNKNOWN
            return

        recent = self.checks[-10:]

        passed = sum(
            1
            for check in recent
            if check.passed
        )

        failed = len(recent) - passed

        if failed == 0:
            self.state = HealthState.HEALTHY
        elif passed == 0:
            self.state = HealthState.FAILED
        else:
            self.state = HealthState.DEGRADED
