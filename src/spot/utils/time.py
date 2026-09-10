"""Time utilities for SPOT."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional


UTC = timezone.utc


def now_utc() -> datetime:
    """Return the current timezone-aware UTC time."""
    return datetime.now(UTC)


def timestamp() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return now_utc().isoformat()


def ensure_utc(value: datetime) -> datetime:
    """Return a timezone-aware UTC datetime."""
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)

    return value.astimezone(UTC)


def parse_timestamp(value: str) -> datetime:
    """Parse an ISO-8601 timestamp and normalize it to UTC."""
    parsed = datetime.fromisoformat(value)

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)

    return parsed.astimezone(UTC)


def seconds_since(value: datetime) -> float:
    """Return seconds elapsed since a datetime."""
    return max(
        0.0,
        (now_utc() - ensure_utc(value)).total_seconds(),
    )


def add_seconds(
    value: datetime,
    seconds: float,
) -> datetime:
    """Add seconds to a datetime."""
    return ensure_utc(value) + timedelta(seconds=seconds)


def add_minutes(
    value: datetime,
    minutes: float,
) -> datetime:
    """Add minutes to a datetime."""
    return add_seconds(value, minutes * 60.0)


def add_hours(
    value: datetime,
    hours: float,
) -> datetime:
    """Add hours to a datetime."""
    return add_seconds(value, hours * 3600.0)


def clamp_datetime(
    value: datetime,
    minimum: Optional[datetime] = None,
    maximum: Optional[datetime] = None,
) -> datetime:
    """Clamp a datetime to an optional range."""
    value = ensure_utc(value)

    if minimum is not None:
        minimum = ensure_utc(minimum)
        if value < minimum:
            value = minimum

    if maximum is not None:
        maximum = ensure_utc(maximum)
        if value > maximum:
            value = maximum

    return value


def duration_seconds(
    start: datetime,
    end: Optional[datetime] = None,
) -> float:
    """Return the duration between two datetimes."""
    start = ensure_utc(start)

    if end is None:
        end = now_utc()
    else:
        end = ensure_utc(end)

    return max(0.0, (end - start).total_seconds())
