"""Bounded randomization utilities for SPOT."""

from __future__ import annotations

import secrets
from typing import Iterable, Sequence, TypeVar


T = TypeVar("T")


def random_float(
    minimum: float = 0.0,
    maximum: float = 1.0,
) -> float:
    """Return a cryptographically generated random float.

    The function is intended for unpredictable seed material and
    bounded random choices, not for security protocol construction.
    """
    if minimum > maximum:
        raise ValueError("minimum cannot exceed maximum.")

    value = secrets.randbits(53) / (2**53)
    return minimum + (maximum - minimum) * value


def random_int(
    minimum: int,
    maximum: int,
) -> int:
    """Return a cryptographically generated random integer."""
    if minimum > maximum:
        raise ValueError("minimum cannot exceed maximum.")

    return secrets.randbelow(maximum - minimum + 1) + minimum


def chance(probability: float) -> bool:
    """Return True according to a probability between 0 and 1."""
    if not 0.0 <= probability <= 1.0:
        raise ValueError(
            "probability must be between 0 and 1."
        )

    return random_float() < probability


def choose(
    values: Sequence[T],
) -> T:
    """Choose one item from a non-empty sequence."""
    if not values:
        raise ValueError("Cannot choose from an empty sequence.")

    return values[random_int(0, len(values) - 1)]


def shuffle(values: Iterable[T]) -> list[T]:
    """Return a shuffled copy of an iterable."""
    result = list(values)

    for index in range(len(result) - 1, 0, -1):
        swap_index = random_int(0, index)
        result[index], result[swap_index] = (
            result[swap_index],
            result[index],
        )

    return result


def bounded_variation(
    value: float,
    variation: float,
    minimum: float,
    maximum: float,
) -> float:
    """Apply bounded random variation to a numeric value."""
    if variation < 0:
        raise ValueError("variation cannot be negative.")

    if minimum > maximum:
        raise ValueError("minimum cannot exceed maximum.")

    delta = random_float(-variation, variation)
    return max(minimum, min(maximum, value + delta))


def random_delay(
    minimum_seconds: float,
    maximum_seconds: float,
) -> float:
    """Return a bounded random delay."""
    if minimum_seconds < 0 or maximum_seconds < 0:
        raise ValueError("Delays cannot be negative.")

    if minimum_seconds > maximum_seconds:
        raise ValueError(
            "minimum_seconds cannot exceed maximum_seconds."
        )

    return random_float(
        minimum_seconds,
        maximum_seconds,
    )
