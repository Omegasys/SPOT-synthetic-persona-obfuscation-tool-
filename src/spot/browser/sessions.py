"""SPOT browser sessions."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any


@dataclass
class BrowserSession:
    """Represents one isolated browser session."""

    profile_id: str
    session_id: str = field(
        default_factory=lambda: uuid.uuid4().hex
    )

    started_at: datetime | None = None
    stopped_at: datetime | None = None

    active: bool = False

    page_count: int = 0
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def start(self) -> None:
        """Start the browser session."""
        if self.active:
            return

        self.started_at = datetime.now(
            timezone.utc
        )
        self.stopped_at = None
        self.active = True

    def stop(self) -> None:
        """Stop the browser session."""
        if not self.active:
            return

        self.stopped_at = datetime.now(
            timezone.utc
        )
        self.active = False

    def record_page(self) -> None:
        """Record a synthetic page visit."""
        if not self.active:
            raise RuntimeError(
                "Cannot record a page on an inactive session."
            )

        self.page_count += 1

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """Store non-sensitive session metadata."""
        self.metadata[key] = value

    def duration_seconds(self) -> float:
        """Return session duration in seconds."""
        if self.started_at is None:
            return 0.0

        end = (
            self.stopped_at
            or datetime.now(timezone.utc)
        )

        return max(
            0.0,
            (end - self.started_at).total_seconds(),
        )
