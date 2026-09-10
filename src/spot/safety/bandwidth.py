from __future__ import annotations

from dataclasses import dataclass, field
from time import time


@dataclass
class BandwidthUsage:
    """Tracks bandwidth usage for a single scope."""

    bytes_sent: int = 0
    bytes_received: int = 0
    started_at: float = field(default_factory=time)
    last_activity: float | None = None

    @property
    def total_bytes(self) -> int:
        """Return total bytes transferred."""
        return self.bytes_sent + self.bytes_received

    @property
    def duration_seconds(self) -> float:
        """Return elapsed tracking time."""
        return max(0.0, time() - self.started_at)

    def record(
        self,
        sent: int = 0,
        received: int = 0,
    ) -> None:
        """Record a bounded bandwidth event."""
        if sent < 0 or received < 0:
            raise ValueError("Bandwidth values cannot be negative.")

        self.bytes_sent += sent
        self.bytes_received += received
        self.last_activity = time()

    def reset(self) -> None:
        """Reset usage counters."""
        self.bytes_sent = 0
        self.bytes_received = 0
        self.started_at = time()
        self.last_activity = None


@dataclass
class BandwidthLimit:
    """Defines bandwidth limits for a scope."""

    max_bytes: int = 100 * 1024 * 1024
    max_bytes_sent: int | None = None
    max_bytes_received: int | None = None
    enabled: bool = True

    def validate(self) -> None:
        """Validate the bandwidth policy."""
        if self.max_bytes < 0:
            raise ValueError("max_bytes cannot be negative.")

        if self.max_bytes_sent is not None and self.max_bytes_sent < 0:
            raise ValueError("max_bytes_sent cannot be negative.")

        if self.max_bytes_received is not None and self.max_bytes_received < 0:
            raise ValueError("max_bytes_received cannot be negative.")


class BandwidthManager:
    """Tracks and limits bandwidth without performing network operations."""

    def __init__(self, default_limit: BandwidthLimit | None = None) -> None:
        self.default_limit = default_limit or BandwidthLimit()
        self.default_limit.validate()

        self._limits: dict[str, BandwidthLimit] = {}
        self._usage: dict[str, BandwidthUsage] = {}

    def set_limit(self, scope: str, limit: BandwidthLimit) -> None:
        """Set a bandwidth limit for a scope."""
        if not scope:
            raise ValueError("scope cannot be empty.")

        limit.validate()
        self._limits[scope] = limit

    def get_limit(self, scope: str) -> BandwidthLimit:
        """Return the limit for a scope."""
        return self._limits.get(scope, self.default_limit)

    def usage(self, scope: str) -> BandwidthUsage:
        """Return usage state for a scope."""
        if not scope:
            raise ValueError("scope cannot be empty.")

        if scope not in self._usage:
            self._usage[scope] = BandwidthUsage()

        return self._usage[scope]

    def can_transfer(
        self,
        scope: str,
        sent: int = 0,
        received: int = 0,
    ) -> bool:
        """Check whether a transfer remains within policy."""
        if sent < 0 or received < 0:
            return False

        limit = self.get_limit(scope)

        if not limit.enabled:
            return False

        current = self.usage(scope)

        if current.total_bytes + sent + received > limit.max_bytes:
            return False

        if (
            limit.max_bytes_sent is not None
            and current.bytes_sent + sent > limit.max_bytes_sent
        ):
            return False

        if (
            limit.max_bytes_received is not None
            and current.bytes_received + received > limit.max_bytes_received
        ):
            return False

        return True

    def record(
        self,
        scope: str,
        sent: int = 0,
        received: int = 0,
    ) -> bool:
        """Record a transfer if it is permitted."""
        if not self.can_transfer(scope, sent, received):
            return False

        self.usage(scope).record(sent=sent, received=received)
        return True

    def remaining(self, scope: str) -> int:
        """Return remaining total bandwidth."""
        limit = self.get_limit(scope)
        current = self.usage(scope)

        return max(0, limit.max_bytes - current.total_bytes)

    def reset(self, scope: str | None = None) -> None:
        """Reset one scope or all scopes."""
        if scope is None:
            for usage in self._usage.values():
                usage.reset()
            return

        self.usage(scope).reset()

    def remove_scope(self, scope: str) -> None:
        """Remove usage and custom policy for a scope."""
        self._usage.pop(scope, None)
        self._limits.pop(scope, None)

    def summary(self, scope: str) -> dict[str, int | float | bool]:
        """Return a safe usage summary."""
        usage = self.usage(scope)
        limit = self.get_limit(scope)

        return {
            "enabled": limit.enabled,
            "bytes_sent": usage.bytes_sent,
            "bytes_received": usage.bytes_received,
            "total_bytes": usage.total_bytes,
            "remaining_bytes": self.remaining(scope),
            "duration_seconds": usage.duration_seconds,
        }
