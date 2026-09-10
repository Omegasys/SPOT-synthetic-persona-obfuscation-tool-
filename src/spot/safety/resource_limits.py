from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ResourceLimits:
    """Defines bounded resource usage for a SPOT session."""

    max_processes: int = 20
    max_browser_instances: int = 3
    max_browser_pages: int = 100
    max_sessions: int = 10
    max_personas: int = 3
    max_memory_mb: int = 2048
    max_cpu_percent: float = 80.0
    max_runtime_seconds: int = 3600
    enabled: bool = True

    def validate(self) -> None:
        """Validate resource limits."""
        integer_limits = {
            "max_processes": self.max_processes,
            "max_browser_instances": self.max_browser_instances,
            "max_browser_pages": self.max_browser_pages,
            "max_sessions": self.max_sessions,
            "max_personas": self.max_personas,
            "max_memory_mb": self.max_memory_mb,
            "max_runtime_seconds": self.max_runtime_seconds,
        }

        for name, value in integer_limits.items():
            if value < 0:
                raise ValueError(f"{name} cannot be negative.")

        if not 0 <= self.max_cpu_percent <= 100:
            raise ValueError("max_cpu_percent must be between 0 and 100.")


@dataclass
class ResourceUsage:
    """Current resource usage for a scope."""

    processes: int = 0
    browser_instances: int = 0
    browser_pages: int = 0
    sessions: int = 0
    personas: int = 0
    memory_mb: int = 0
    cpu_percent: float = 0.0
    runtime_seconds: float = 0.0
    metadata: dict[str, object] = field(default_factory=dict)

    def reset(self) -> None:
        """Reset usage counters."""
        self.processes = 0
        self.browser_instances = 0
        self.browser_pages = 0
        self.sessions = 0
        self.personas = 0
        self.memory_mb = 0
        self.cpu_percent = 0.0
        self.runtime_seconds = 0.0
        self.metadata.clear()


class ResourceLimitManager:
    """Tracks resource usage and enforces declared limits."""

    def __init__(self, default_limits: ResourceLimits | None = None) -> None:
        self.default_limits = default_limits or ResourceLimits()
        self.default_limits.validate()

        self._limits: dict[str, ResourceLimits] = {}
        self._usage: dict[str, ResourceUsage] = {}

    def set_limits(self, scope: str, limits: ResourceLimits) -> None:
        """Set resource limits for a scope."""
        if not scope:
            raise ValueError("scope cannot be empty.")

        limits.validate()
        self._limits[scope] = limits

    def get_limits(self, scope: str) -> ResourceLimits:
        """Return limits for a scope."""
        return self._limits.get(scope, self.default_limits)

    def usage(self, scope: str) -> ResourceUsage:
        """Return usage state for a scope."""
        if not scope:
            raise ValueError("scope cannot be empty.")

        if scope not in self._usage:
            self._usage[scope] = ResourceUsage()

        return self._usage[scope]

    def within_limits(
        self,
        scope: str,
        usage: ResourceUsage | None = None,
    ) -> bool:
        """Check whether supplied or current usage is within limits."""
        limits = self.get_limits(scope)

        if not limits.enabled:
            return False

        current = usage or self.usage(scope)

        return (
            current.processes <= limits.max_processes
            and current.browser_instances <= limits.max_browser_instances
            and current.browser_pages <= limits.max_browser_pages
            and current.sessions <= limits.max_sessions
            and current.personas <= limits.max_personas
            and current.memory_mb <= limits.max_memory_mb
            and current.cpu_percent <= limits.max_cpu_percent
            and current.runtime_seconds <= limits.max_runtime_seconds
        )

    def update(
        self,
        scope: str,
        *,
        processes: int | None = None,
        browser_instances: int | None = None,
        browser_pages: int | None = None,
        sessions: int | None = None,
        personas: int | None = None,
        memory_mb: int | None = None,
        cpu_percent: float | None = None,
        runtime_seconds: float | None = None,
    ) -> bool:
        """Update usage if the resulting state remains within limits."""
        current = self.usage(scope)

        candidate = ResourceUsage(
            processes=current.processes if processes is None else processes,
            browser_instances=(
                current.browser_instances
                if browser_instances is None
                else browser_instances
            ),
            browser_pages=(
                current.browser_pages
                if browser_pages is None
                else browser_pages
            ),
            sessions=current.sessions if sessions is None else sessions,
            personas=current.personas if personas is None else personas,
            memory_mb=current.memory_mb if memory_mb is None else memory_mb,
            cpu_percent=current.cpu_percent if cpu_percent is None else cpu_percent,
            runtime_seconds=(
                current.runtime_seconds
                if runtime_seconds is None
                else runtime_seconds
            ),
            metadata=dict(current.metadata),
        )

        values = (
            candidate.processes,
            candidate.browser_instances,
            candidate.browser_pages,
            candidate.sessions,
            candidate.personas,
            candidate.memory_mb,
            candidate.cpu_percent,
            candidate.runtime_seconds,
        )

        if any(value < 0 for value in values):
            return False

        if not self.within_limits(scope, candidate):
            return False

        self._usage[scope] = candidate
        return True

    def increment(
        self,
        scope: str,
        *,
        processes: int = 0,
        browser_instances: int = 0,
        browser_pages: int = 0,
        sessions: int = 0,
        personas: int = 0,
        memory_mb: int = 0,
        cpu_percent: float = 0.0,
        runtime_seconds: float = 0.0,
    ) -> bool:
        """Increase usage while respecting limits."""
        current = self.usage(scope)

        return self.update(
            scope,
            processes=current.processes + processes,
            browser_instances=(
                current.browser_instances + browser_instances
            ),
            browser_pages=current.browser_pages + browser_pages,
            sessions=current.sessions + sessions,
            personas=current.personas + personas,
            memory_mb=current.memory_mb + memory_mb,
            cpu_percent=cpu_percent,
            runtime_seconds=current.runtime_seconds + runtime_seconds,
        )

    def reset(self, scope: str | None = None) -> None:
        """Reset one scope or all scopes."""
        if scope is None:
            for usage in self._usage.values():
                usage.reset()
            return

        self.usage(scope).reset()

    def summary(self, scope: str) -> dict[str, int | float | bool]:
        """Return current resource usage."""
        usage = self.usage(scope)
        limits = self.get_limits(scope)

        return {
            "enabled": limits.enabled,
            "within_limits": self.within_limits(scope),
            "processes": usage.processes,
            "browser_instances": usage.browser_instances,
            "browser_pages": usage.browser_pages,
            "sessions": usage.sessions,
            "personas": usage.personas,
            "memory_mb": usage.memory_mb,
            "cpu_percent": usage.cpu_percent,
            "runtime_seconds": usage.runtime_seconds,
        }
