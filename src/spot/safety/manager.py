"""SPOT safety manager."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

from .allowlist import Allowlist
from .blocklist import Blocklist
from .limits import SafetyLimits, UsageTracker
from .rate_limit import RateLimitPolicy, RateLimiter


@dataclass
class SafetyDecision:
    """Result of a SPOT safety check."""

    allowed: bool
    reason: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


class SafetyManager:
    """Coordinate SPOT safety controls."""

    def __init__(
        self,
        limits: SafetyLimits | None = None,
        allowlist: Allowlist | None = None,
        blocklist: Blocklist | None = None,
        rate_limiter: RateLimiter | None = None,
    ) -> None:
        self.limits = (
            limits
            or SafetyLimits()
        )

        self.allowlist = (
            allowlist
            or Allowlist()
        )

        self.blocklist = (
            blocklist
            or Blocklist()
        )

        self.rate_limiter = (
            rate_limiter
            or RateLimiter(
                RateLimitPolicy()
            )
        )

        self.usage = UsageTracker(
            self.limits
        )

        self.enabled = True
        self.emergency_stop = False

    def check(
        self,
        action: str,
        target: str | None = None,
        amount: int = 1,
        persona_id: str | None = None,
    ) -> SafetyDecision:
        """Perform all applicable safety checks."""

        if not self.enabled:
            return SafetyDecision(
                allowed=False,
                reason="Safety manager is disabled.",
            )

        if self.emergency_stop:
            return SafetyDecision(
                allowed=False,
                reason="SPOT emergency stop is active.",
            )

        if not action:
            return SafetyDecision(
                allowed=False,
                reason="Action cannot be empty.",
            )

        if self.blocklist.contains(action):
            return SafetyDecision(
                allowed=False,
                reason=f"Action is blocked: {action}",
            )

        if target is not None:
            if self.blocklist.matches(target):
                return SafetyDecision(
                    allowed=False,
                    reason=f"Target is blocked: {target}",
                )

            if (
                self.allowlist.enabled
                and not self.allowlist.matches(target)
            ):
                return SafetyDecision(
                    allowed=False,
                    reason=f"Target is not allowlisted: {target}",
                )

        if not self.usage.within_limits(
            action,
            amount,
            persona_id=persona_id,
        ):
            return SafetyDecision(
                allowed=False,
                reason="Safety usage limit exceeded.",
            )

        if not self.rate_limiter.allow(
            action,
            amount=amount,
        ):
            return SafetyDecision(
                allowed=False,
                reason="Safety rate limit exceeded.",
            )

        return SafetyDecision(
            allowed=True,
            reason="Action passed SPOT safety checks.",
        )

    def record(
        self,
        action: str,
        amount: int = 1,
        persona_id: str | None = None,
    ) -> None:
        """Record permitted activity."""
        self.usage.record(
            action,
            amount=amount,
            persona_id=persona_id,
        )

    def activate_emergency_stop(
        self,
    ) -> None:
        """Activate the SPOT safety emergency stop."""
        self.emergency_stop = True

    def reset_emergency_stop(
        self,
    ) -> None:
        """Reset the emergency stop."""
        self.emergency_stop = False
        self.rate_limiter.reset()

    def disable(self) -> None:
        """Disable safety-controlled activity."""
        self.enabled = False

    def enable(self) -> None:
        """Enable safety-controlled activity."""
        self.enabled = True

    def reset_usage(self) -> None:
        """Reset usage counters."""
        self.usage.reset()

    def summary(self) -> Dict[str, Any]:
        """Return the current safety state."""
        return {
            "enabled": self.enabled,
            "emergency_stop": self.emergency_stop,
            "usage": self.usage.summary(),
            "allowlist_enabled": (
                self.allowlist.enabled
            ),
            "blocklist_enabled": (
                self.blocklist.enabled
            ),
            "rate_limiter_enabled": (
                self.rate_limiter.policy.enabled
            ),
        }
