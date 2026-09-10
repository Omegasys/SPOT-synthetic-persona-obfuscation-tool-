"""SPOT scheduler timers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict


@dataclass
class Timer:
    """A scheduler timer."""

    timer_id: str
    interval_seconds: float

    next_run: datetime | None = None
    enabled: bool = True

    def schedule(
        self,
        now: datetime | None = None,
    ) -> datetime:
        """Schedule the next timer execution."""
        current = now or datetime.now(timezone.utc)

        self.next_run = (
            current
            + timedelta(
                seconds=self.interval_seconds
            )
        )

        return self.next_run

    def due(
        self,
        now: datetime | None = None,
    ) -> bool:
        """Return whether the timer is due."""
        if not self.enabled:
            return False

        if self.next_run is None:
            return False

        current = now or datetime.now(timezone.utc)

        return self.next_run <= current


class TimerManager:
    """Manage bounded scheduler timers."""

    def __init__(
        self,
        max_timers: int = 100,
    ) -> None:
        self.max_timers = max_timers

        self.timers: Dict[
            str,
            Timer,
        ] = {}

    def create(
        self,
        timer_id: str,
        interval_seconds: float,
    ) -> Timer:
        """Create a timer."""
        if len(self.timers) >= self.max_timers:
            raise RuntimeError(
                "Maximum number of timers reached."
            )

        if timer_id in self.timers:
            raise ValueError(
                f"Timer already exists: {timer_id}"
            )

        if interval_seconds <= 0:
            raise ValueError(
                "Timer interval must be positive."
            )

        timer = Timer(
            timer_id=timer_id,
            interval_seconds=interval_seconds,
        )

        self.timers[timer_id] = timer

        return timer

    def get(
        self,
        timer_id: str,
    ) -> Timer | None:
        """Return a timer."""
        return self.timers.get(timer_id)

    def require(
        self,
        timer_id: str,
    ) -> Timer:
        """Return a timer or raise an error."""
        timer = self.get(timer_id)

        if timer is None:
            raise KeyError(
                f"Unknown timer: {timer_id}"
            )

        return timer

    def remove(
        self,
        timer_id: str,
    ) -> None:
        """Remove a timer."""
        self.require(timer_id)
        del self.timers[timer_id]

    def due(
        self,
        now: datetime | None = None,
    ) -> list[Timer]:
        """Return timers that are due."""
        return [
            timer
            for timer in self.timers.values()
            if timer.due(now)
        ]

    def reset(
        self,
        now: datetime | None = None,
    ) -> None:
        """Reschedule all enabled timers."""
        for timer in self.timers.values():
            if timer.enabled:
                timer.schedule(now)
