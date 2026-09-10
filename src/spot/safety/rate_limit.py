"""SPOT safety rate limiting."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict


@dataclass
class RateLimit:
    """Rate limit for one activity category."""

    maximum: int
    window_seconds: float

    def validate(self) -> None:
        """Validate rate-limit settings."""
        if self.maximum < 1:
            raise ValueError(
                "Rate limit maximum must be at least 1."
            )

        if self.window_seconds <= 0:
            raise ValueError(
                "Rate limit window must be positive."
            )


@dataclass
class RateLimitPolicy:
    """SPOT rate-limit policy."""

    enabled: bool = True

    default: RateLimit = field(
        default_factory=lambda: RateLimit(
            maximum=30,
            window_seconds=60,
        )
    )

    limits: Dict[
        str,
        RateLimit,
    ] = field(
        default_factory=dict
    )


class RateLimiter:
    """Apply bounded sliding-window rate limits."""

    def __init__(
        self,
        policy: RateLimitPolicy | None = None,
    ) -> None:
        self.policy = (
            policy
            or RateLimitPolicy()
        )

        self.history: Dict[
            str,
            list[datetime],
        ] = {}

        self._validate()

    def _validate(self) -> None:
        """Validate the complete policy."""
        self.policy.default.validate()

        for limit in self.policy.limits.values():
            limit.validate()

    def allow(
        self,
        category: str,
        amount: int = 1,
        now: datetime | None = None,
    ) -> bool:
        """Check whether an action is within its rate limit."""
        if not self.policy.enabled:
            return False

        if amount < 1:
            raise ValueError(
                "Rate-limit amount must be at least 1."
            )

        current = (
            now
            or datetime.now(timezone.utc)
        )

        limit = self.policy.limits.get(
            category,
            self.policy.default,
        )

        cutoff = (
            current
            - timedelta(
                seconds=limit.window_seconds
            )
        )

        history = self.history.setdefault(
            category,
            [],
        )

        history[:] = [
            timestamp
            for timestamp in history
            if timestamp > cutoff
        ]

        if len(history) + amount > limit.maximum:
            return False

        history.extend(
            [current] * amount
        )

        return True

    def remaining(
        self,
        category: str,
        now: datetime | None = None,
    ) -> int:
        """Return remaining operations in the current window."""
        current = (
            now
            or datetime.now(timezone.utc)
        )

        limit = self.policy.limits.get(
            category,
            self.policy.default,
        )

        cutoff = (
            current
            - timedelta(
                seconds=limit.window_seconds
            )
        )

        history = self.history.get(
            category,
            [],
        )

        active = sum(
            1
            for timestamp in history
            if timestamp > cutoff
        )

        return max(
            0,
            limit.maximum - active,
        )

    def reset(
        self,
        category: str | None = None,
    ) -> None:
        """Reset rate-limit history."""
        if category is None:
            self.history.clear()
            return

        self.history.pop(
            category,
            None,
        )

    def summary(self) -> dict:
        """Return current rate-limit state."""
        return {
            category: len(timestamps)
            for category, timestamps
            in self.history.items()
        }
