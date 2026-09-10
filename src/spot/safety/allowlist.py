"""SPOT safety allowlists."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List


@dataclass
class Allowlist:
    """Explicit allowlist for destinations."""

    enabled: bool = False

    entries: List[str] = field(
        default_factory=list
    )

    def add(
        self,
        value: str,
    ) -> None:
        """Add an allowlist entry."""
        value = self._normalize(value)

        if not value:
            raise ValueError(
                "Allowlist entry cannot be empty."
            )

        if value not in self.entries:
            self.entries.append(value)

    def add_many(
        self,
        values: Iterable[str],
    ) -> None:
        """Add multiple entries."""
        for value in values:
            self.add(value)

    def remove(
        self,
        value: str,
    ) -> None:
        """Remove an entry."""
        value = self._normalize(value)

        self.entries = [
            entry
            for entry in self.entries
            if entry != value
        ]

    def clear(self) -> None:
        """Clear the allowlist."""
        self.entries.clear()

    def matches(
        self,
        value: str,
    ) -> bool:
        """Check whether a value is explicitly allowed."""
        if not self.enabled:
            return True

        normalized = self._normalize(value)

        for entry in self.entries:
            if (
                normalized == entry
                or normalized.endswith(
                    "." + entry
                )
            ):
                return True

        return False

    @staticmethod
    def _normalize(
        value: str,
    ) -> str:
        """Normalize an allowlist value."""
        return (
            str(value)
            .strip()
            .lower()
            .rstrip(".")
        )
