from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from statistics import mean


@dataclass
class NumericStatistics:
    """Basic statistics for a numeric dataset."""

    count: int = 0
    minimum: float | None = None
    maximum: float | None = None
    average: float | None = None
    total: float = 0.0

    @classmethod
    def from_values(
        cls,
        values: list[float],
    ) -> "NumericStatistics":
        """Calculate statistics from numeric values."""
        if not values:
            return cls()

        return cls(
            count=len(values),
            minimum=min(values),
            maximum=max(values),
            average=mean(values),
            total=sum(values),
        )

    def to_dict(self) -> dict[str, float | int | None]:
        return {
            "count": self.count,
            "minimum": self.minimum,
            "maximum": self.maximum,
            "average": self.average,
            "total": self.total,
        }


@dataclass
class CategoryStatistics:
    """Frequency statistics for categorical values."""

    counts: dict[str, int] = field(default_factory=dict)

    @classmethod
    def from_values(
        cls,
        values: list[str],
    ) -> "CategoryStatistics":
        """Calculate category frequencies."""
        return cls(
            counts=dict(Counter(values))
        )

    @property
    def total(self) -> int:
        return sum(self.counts.values())

    @property
    def unique(self) -> int:
        return len(self.counts)

    def most_common(
        self,
        limit: int = 10,
    ) -> list[tuple[str, int]]:
        """Return the most common categories."""
        if limit < 1:
            raise ValueError("limit must be positive.")

        return Counter(self.counts).most_common(limit)

    def to_dict(self) -> dict[str, object]:
        return {
            "total": self.total,
            "unique": self.unique,
            "counts": dict(self.counts),
        }


class Statistics:
    """Utility methods for aggregate analytics."""

    @staticmethod
    def numeric(values: list[float]) -> NumericStatistics:
        return NumericStatistics.from_values(values)

    @staticmethod
    def categories(values: list[str]) -> CategoryStatistics:
        return CategoryStatistics.from_values(values)

    @staticmethod
    def percentage(
        part: int | float,
        total: int | float,
    ) -> float:
        """Calculate a percentage safely."""
        if total <= 0:
            return 0.0

        return (part / total) * 100.0

    @staticmethod
    def rate(
        count: int | float,
        duration_seconds: float,
    ) -> float:
        """Calculate events per second."""
        if duration_seconds <= 0:
            return 0.0

        return count / duration_seconds
