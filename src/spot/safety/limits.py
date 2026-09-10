"""SPOT safety usage limits."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class SafetyLimits:
    """Hard limits for SPOT activity."""

    max_activities: int = 100
    max_requests: int = 100
    max_dns_queries: int = 100

    max_sessions: int = 10
    max_concurrent_personas: int = 3

    max_runtime_seconds: int = 3600
    max_bandwidth_bytes: int = 100 * 1024 * 1024

    max_browser_pages: int = 100
    max_processes: int = 20

    enabled: bool = True


@dataclass
class UsageState:
    """Current resource usage."""

    activities: int = 0
    requests: int = 0
    dns_queries: int = 0
    sessions: int = 0
    concurrent_personas: int = 0
    runtime_seconds: float = 0.0
    bandwidth_bytes: int = 0
    browser_pages: int = 0
    processes: int = 0


class UsageTracker:
    """Track SPOT resource usage."""

    def __init__(
        self,
        limits: SafetyLimits | None = None,
    ) -> None:
        self.limits = (
            limits
            or SafetyLimits()
        )

        self.state = UsageState()

        self.persona_usage: Dict[
            str,
            UsageState,
        ] = {}

    def within_limits(
        self,
        action: str,
        amount: int = 1,
        persona_id: str | None = None,
    ) -> bool:
        """Check whether an action remains within limits."""
        if not self.limits.enabled:
            return False

        if amount < 0:
            return False

        if persona_id is not None:
            state = self.persona_usage.setdefault(
                persona_id,
                UsageState(),
            )
        else:
            state = self.state

        if action in {
            "activity",
            "activities",
        }:
            return (
                self.state.activities + amount
                <= self.limits.max_activities
            )

        if action in {
            "request",
            "requests",
        }:
            return (
                self.state.requests + amount
                <= self.limits.max_requests
            )

        if action in {
            "dns",
            "dns_query",
            "dns_queries",
        }:
            return (
                self.state.dns_queries + amount
                <= self.limits.max_dns_queries
            )

        if action in {
            "session",
            "sessions",
        }:
            return (
                self.state.sessions + amount
                <= self.limits.max_sessions
            )

        if action in {
            "browser_page",
            "browser_pages",
        }:
            return (
                self.state.browser_pages + amount
                <= self.limits.max_browser_pages
            )

        if action in {
            "process",
            "processes",
        }:
            return (
                self.state.processes + amount
                <= self.limits.max_processes
            )

        # Unknown actions are denied rather than silently
        # bypassing the safety system.
        return False

    def record(
        self,
        action: str,
        amount: int = 1,
        persona_id: str | None = None,
    ) -> None:
        """Record resource usage."""
        if amount < 0:
            raise ValueError(
                "Usage amount cannot be negative."
            )

        state = self.state

        if action in {
            "activity",
            "activities",
        }:
            state.activities += amount

        elif action in {
            "request",
            "requests",
        }:
            state.requests += amount

        elif action in {
            "dns",
            "dns_query",
            "dns_queries",
        }:
            state.dns_queries += amount

        elif action in {
            "session",
            "sessions",
        }:
            state.sessions += amount

        elif action in {
            "browser_page",
            "browser_pages",
        }:
            state.browser_pages += amount

        elif action in {
            "process",
            "processes",
        }:
            state.processes += amount

        else:
            raise ValueError(
                f"Unknown usage type: {action}"
            )

        if persona_id is not None:
            persona_state = (
                self.persona_usage.setdefault(
                    persona_id,
                    UsageState(),
                )
            )

            if action in {
                "activity",
                "activities",
            }:
                persona_state.activities += amount

            elif action in {
                "request",
                "requests",
            }:
                persona_state.requests += amount

            elif action in {
                "dns",
                "dns_query",
                "dns_queries",
            }:
                persona_state.dns_queries += amount

            elif action in {
                "session",
                "sessions",
            }:
                persona_state.sessions += amount

            elif action in {
                "browser_page",
                "browser_pages",
            }:
                persona_state.browser_pages += amount

            elif action in {
                "process",
                "processes",
            }:
                persona_state.processes += amount

    def reset(self) -> None:
        """Reset all usage."""
        self.state = UsageState()
        self.persona_usage.clear()

    def summary(self) -> dict:
        """Return usage information."""
        return {
            "activities": self.state.activities,
            "requests": self.state.requests,
            "dns_queries": self.state.dns_queries,
            "sessions": self.state.sessions,
            "concurrent_personas": (
                self.state.concurrent_personas
            ),
            "runtime_seconds": (
                self.state.runtime_seconds
            ),
            "bandwidth_bytes": (
                self.state.bandwidth_bytes
            ),
            "browser_pages": (
                self.state.browser_pages
            ),
            "processes": self.state.processes,
        }
