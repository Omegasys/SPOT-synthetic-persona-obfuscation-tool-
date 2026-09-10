"""SPOT synthetic activity scheduler."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List

from .calendar import CalendarRule, ScheduleCalendar
from .concurrency import ConcurrencyController
from .randomizer import ScheduleRandomizer
from .timers import TimerManager


@dataclass
class ScheduledJob:
    """A scheduled SPOT job."""

    job_id: str
    persona_id: str
    activity_type: str

    enabled: bool = True

    next_run: datetime | None = None
    last_run: datetime | None = None

    metadata: Dict[str, str] = field(
        default_factory=dict
    )


class Scheduler:
    """Coordinate SPOT scheduled synthetic activity."""

    def __init__(
        self,
        timers: TimerManager | None = None,
        calendar: ScheduleCalendar | None = None,
        randomizer: ScheduleRandomizer | None = None,
        concurrency: ConcurrencyController | None = None,
    ) -> None:
        self.timers = timers or TimerManager()
        self.calendar = calendar or ScheduleCalendar()
        self.randomizer = (
            randomizer
            or ScheduleRandomizer()
        )
        self.concurrency = (
            concurrency
            or ConcurrencyController()
        )

        self.jobs: Dict[str, ScheduledJob] = {}
        self.enabled = False

    def add_job(
        self,
        job: ScheduledJob,
    ) -> None:
        """Add a scheduled job."""
        if job.job_id in self.jobs:
            raise ValueError(
                f"Scheduled job already exists: {job.job_id}"
            )

        self.jobs[job.job_id] = job

    def remove_job(
        self,
        job_id: str,
    ) -> None:
        """Remove a scheduled job."""
        if job_id not in self.jobs:
            raise KeyError(
                f"Unknown scheduled job: {job_id}"
            )

        del self.jobs[job_id]

    def get(
        self,
        job_id: str,
    ) -> ScheduledJob | None:
        """Return a scheduled job."""
        return self.jobs.get(job_id)

    def enable(self) -> None:
        """Enable scheduling."""
        self.enabled = True

    def disable(self) -> None:
        """Disable scheduling."""
        self.enabled = False

    def due(
        self,
        now: datetime | None = None,
    ) -> List[ScheduledJob]:
        """Return jobs that are due to run."""
        if not self.enabled:
            return []

        current = now or datetime.now(timezone.utc)

        return [
            job
            for job in self.jobs.values()
            if job.enabled
            and job.next_run is not None
            and job.next_run <= current
            and self.concurrency.can_start()
        ]

    def schedule_next(
        self,
        job_id: str,
        now: datetime | None = None,
    ) -> datetime:
        """Calculate and store the next execution time."""
        job = self.get(job_id)

        if job is None:
            raise KeyError(
                f"Unknown scheduled job: {job_id}"
            )

        current = now or datetime.now(timezone.utc)

        next_run = self.calendar.next_occurrence(
            current
        )

        next_run = self.randomizer.adjust_datetime(
            next_run
        )

        job.next_run = next_run

        return next_run

    def mark_started(
        self,
        job_id: str,
        now: datetime | None = None,
    ) -> None:
        """Mark a job as started."""
        job = self.get(job_id)

        if job is None:
            raise KeyError(
                f"Unknown scheduled job: {job_id}"
            )

        if not self.concurrency.start():
            raise RuntimeError(
                "Maximum scheduler concurrency reached."
            )

        job.last_run = (
            now
            or datetime.now(timezone.utc)
        )

    def mark_finished(
        self,
        job_id: str,
    ) -> None:
        """Mark a job as finished."""
        job = self.get(job_id)

        if job is None:
            raise KeyError(
                f"Unknown scheduled job: {job_id}"
            )

        self.concurrency.finish()

        if job.enabled:
            self.schedule_next(job_id)

    def stop_all(self) -> None:
        """Stop scheduling and clear active concurrency."""
        self.disable()
        self.concurrency.reset()

    def active_jobs(self) -> List[ScheduledJob]:
        """Return enabled scheduled jobs."""
        return [
            job
            for job in self.jobs.values()
            if job.enabled
        ]
