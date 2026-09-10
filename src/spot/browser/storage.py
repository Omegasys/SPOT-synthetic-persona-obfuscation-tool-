"""SPOT isolated browser storage."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class BrowserStorage:
    """Isolated local/session storage for a synthetic profile."""

    enabled: bool = True
    persistent: bool = True

    max_entries: int = 250

    local: Dict[str, Any] = field(
        default_factory=dict
    )
    session: Dict[str, Any] = field(
        default_factory=dict
    )

    def set_local(
        self,
        key: str,
        value: Any,
    ) -> None:
        """Set a local storage value."""
        if not self.enabled:
            return

        self.local[key] = value
        self._enforce_limit(self.local)

    def set_session(
        self,
        key: str,
        value: Any,
    ) -> None:
        """Set a session storage value."""
        if not self.enabled:
            return

        self.session[key] = value
        self._enforce_limit(self.session)

    def get_local(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """Read a local storage value."""
        if not self.enabled:
            return default

        return self.local.get(
            key,
            default,
        )

    def get_session(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """Read a session storage value."""
        if not self.enabled:
            return default

        return self.session.get(
            key,
            default,
        )

    def delete_local(
        self,
        key: str,
    ) -> None:
        """Delete a local storage value."""
        self.local.pop(key, None)

    def delete_session(
        self,
        key: str,
    ) -> None:
        """Delete a session storage value."""
        self.session.pop(key, None)

    def clear_local(self) -> None:
        """Clear local storage."""
        self.local.clear()

    def clear_session(self) -> None:
        """Clear session storage."""
        self.session.clear()

    def clear_all(self) -> None:
        """Clear all browser storage."""
        self.clear_local()
        self.clear_session()

    def _enforce_limit(
        self,
        storage: Dict[str, Any],
    ) -> None:
        """Enforce the maximum number of entries."""
        while len(storage) > self.max_entries:
            oldest_key = next(iter(storage))
            del storage[oldest_key]
