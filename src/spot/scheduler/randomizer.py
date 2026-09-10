"""SPOT bounded schedule randomization."""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Iterable, TypeVar


T = TypeVar("T")


class ScheduleRandomizer:
    """Apply bounded variation to scheduler decisions."""

    def __init__(
        self,
        max_delay_seconds: int = 900,
        seed: int | None = None,
    ) -> None:
        if max_delay_seconds < 0:
            raise ValueError(
                "Maximum delay cannot be negative."
            )

        self.max_delay_seconds = max_delay_seconds
        self.random = random.Random(seed)

    def delay_seconds(
        self,
        maximum: int | None = None,
    ) -> float:
        """Return a bounded random delay."""
        maximum = (
            self.max_delay_seconds
            if maximum is None
            else max(0, maximum)
        )

        return self.random.uniform(
            0,
            maximum,
        )

    def adjust_datetime(
        self,
        value: datetime,
        maximum_seconds: int | None = None,
    ) -> datetime:
        """Apply bounded timing variation."""
        delay = self.delay_seconds(
            maximum_seconds
        )

        return value + timedelta(
            seconds=delay
        )

    def choose(
        self,
        values: Iterable[T],
    ) -> T:
        """Choose one item from a collection."""
        options = list(values)

        if not options:
            raise ValueError(
                "Cannot choose from an empty collection."
            )

        return self.random.choice(options)

    def shuffle(
        self,
        values: Iterable[T],
    ) -> list[T]:
        """Return a shuffled copy."""
        result = list(values)
        self.random.shuffle(result)
        return result

    def chance(
        self,
        probability: float,
    ) -> bool:
        """Perform a bounded probability check."""
        probability = max(
            0.0,
            min(1.0, float(probability)),
        )

        return (
            self.random.random()
            < probability
        )
