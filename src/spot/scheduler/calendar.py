"""SPOT scheduler calendar rules."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import List


@dataclass
class CalendarRule:
    """A recurring calendar rule."""

    days: List[str] = field(
        default_factory=list
    )

    preferred_hour: int = 12
    preferred_minute: int = 0

    enabled: bool = True

    def validate(self) -> None:
        """Validate the calendar rule."""
        if not 0 <= self.preferred_hour <= 23:
            raise ValueError(
                "Preferred hour must be between 0 and 23."
            )

        if not 0 <= self.preferred_minute <= 59:
            raise ValueError(
                "Preferred minute must be between 0 and 59."
            )

        valid_days = {
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        }

        for day in self.days:
            if day.lower() not in valid_days:
                raise ValueError(
                    f"Invalid calendar day: {day}"
                )


class ScheduleCalendar:
    """Calculate future schedule occurrences."""

    def __init__(
        self,
        rule: CalendarRule | None = None,
    ) -> None:
        self.rule = (
            rule
            or CalendarRule()
        )

    def next_occurrence(
        self,
        now: datetime | None = None,
    ) -> datetime:
        """Return the next calendar occurrence."""
        self.rule.validate()

        current = now or datetime.now(timezone.utc)

        if not self.rule.enabled:
            raise RuntimeError(
                "Calendar rule is disabled."
            )

        days = [
            day.lower()
            for day in self.rule.days
        ]

        # Empty day list means every day.
        if not days:
            allowed_weekdays = set(
                range(7)
            )
        else:
            names = [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ]

            allowed_weekdays = {
                names.index(day)
                for day in days
            }

        for offset in range(8):
            candidate_date = (
                current.date()
                + timedelta(days=offset)
            )

            if (
                candidate_date.weekday()
                not in allowed_weekdays
            ):
                continue

            candidate = datetime(
                candidate_date.year,
                candidate_date.month,
                candidate_date.day,
                self.rule.preferred_hour,
                self.rule.preferred_minute,
                tzinfo=current.tzinfo,
            )

            if candidate > current:
                return candidate

        raise RuntimeError(
            "Unable to calculate next calendar occurrence."
        )

    def matches(
        self,
        value: datetime,
    ) -> bool:
        """Return whether a datetime matches the rule."""
        self.rule.validate()

        if not self.rule.enabled:
            return False

        if self.rule.days:
            if (
                value.strftime("%A").lower()
                not in [
                    day.lower()
                    for day in self.rule.days
                ]
            ):
                return False

        return (
            value.hour
            == self.rule.preferred_hour
            and value.minute
            == self.rule.preferred_minute
        )
