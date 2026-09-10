"""SPOT bounded behavioral randomization."""

from __future__ import annotations

import random
from typing import Iterable, TypeVar


T = TypeVar("T")


class Randomization:
    """Provide controlled variation for synthetic behavior."""

    def __init__(
        self,
        seed: int | None = None,
    ) -> None:
        self.random = random.Random(seed)

    def vary(
        self,
        value: float,
        variation: float = 0.10,
    ) -> float:
        """Apply bounded multiplicative variation."""
        variation = max(
            0.0,
            min(1.0, float(variation)),
        )

        minimum = 1.0 - variation
        maximum = 1.0 + variation

        result = value * self.random.uniform(
            minimum,
            maximum,
        )

        return max(0.0, result)

    def bounded(
        self,
        value: float,
        minimum: float,
        maximum: float,
        variation: float = 0.10,
    ) -> float:
        """Randomize a value while preserving hard bounds."""
        result = self.vary(
            value,
            variation,
        )

        return max(
            minimum,
            min(maximum, result),
        )

    def choose_with_variation(
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

    def chance(
        self,
        probability: float,
        variation: float = 0.05,
    ) -> bool:
        """Perform a bounded randomized probability check."""
        adjusted = self.bounded(
            probability,
            0.0,
            1.0,
            variation,
        )

        return self.random.random() < adjusted
