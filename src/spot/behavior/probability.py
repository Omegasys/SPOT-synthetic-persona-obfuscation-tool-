"""SPOT probability utilities."""

from __future__ import annotations

import random
from typing import Dict, Iterable, TypeVar


T = TypeVar("T")


class ProbabilityModel:
    """Perform bounded weighted random selection."""

    def __init__(
        self,
        seed: int | None = None,
    ) -> None:
        self.random = random.Random(seed)

    def choose(
        self,
        weights: Dict[T, float],
    ) -> T:
        """Choose one item according to its weight."""
        if not weights:
            raise ValueError(
                "Cannot choose from an empty weight set."
            )

        items = []
        values = []

        for item, weight in weights.items():
            weight = max(0.0, float(weight))

            if weight <= 0:
                continue

            items.append(item)
            values.append(weight)

        if not items:
            raise ValueError(
                "All probability weights are zero."
            )

        return self.random.choices(
            items,
            weights=values,
            k=1,
        )[0]

    def chance(
        self,
        probability: float,
    ) -> bool:
        """Return True according to a bounded probability."""
        probability = max(
            0.0,
            min(1.0, float(probability)),
        )

        return self.random.random() < probability

    def random_float(
        self,
        minimum: float = 0.0,
        maximum: float = 1.0,
    ) -> float:
        """Return a random float in a bounded range."""
        if minimum > maximum:
            raise ValueError(
                "Minimum cannot exceed maximum."
            )

        return self.random.uniform(
            minimum,
            maximum,
        )

    def shuffle(
        self,
        values: Iterable[T],
    ) -> list[T]:
        """Return a shuffled copy of an iterable."""
        result = list(values)
        self.random.shuffle(result)
        return result
