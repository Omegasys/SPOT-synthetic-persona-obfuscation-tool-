"""SPOT safety blocklists."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List


@dataclass
class Blocklist:
    """Explicit blocklist for unsafe actions or destinations."""

    enabled: bool = True

    entries: List[str] = field(
        default_factory=lambda: [
            "credential_theft",
            "credential_access",
            "auth_bypass",
            "captcha_bypass",
            "security_control_bypass",
            "dos",
            "ddos",
            "spam",
            "bulk_messaging",
            "harassment",
            "fraud",
            "impersonation",
        ]
    )

    def add(
        self,
        value: str,
    ) -> None:
        """Add a blocklist entry."""
        value = self._normalize(value)

        if not value:
            raise ValueError(
                "Blocklist entry cannot be empty."
            )

        if value not in self.entries:
            self.entries.append(value)

    def add_many(
        self,
        values: Iterable[str],
    ) -> None:
        """Add multiple blocklist entries."""
        for value in values:
            self.add(value)

    def remove(
        self,
        value: str,
    ) -> None:
        """Remove a blocklist entry."""
        value = self._normalize(value)

        self.entries = [
            entry
            for entry in self.entries
            if entry != value
        ]

    def contains(
        self,
        value: str,
    ) -> bool:
        """Check for an exact blocked action."""
        if not self.enabled:
            return False

        normalized = self._normalize(value)

        return normalized in self.entries

    def matches(
        self,
        value: str,
    ) -> bool:
        """Check whether a destination is blocked."""
        if not self.enabled:
            return False

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

    def clear(self) -> None:
        """Clear custom blocklist entries."""
        self.entries.clear()

    @staticmethod
    def _normalize(
        value: str,
    ) -> str:
        """Normalize a blocklist value."""
        return (
            str(value)
            .strip()
            .lower()
            .rstrip(".")
        )
