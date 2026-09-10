"""SPOT synthetic behavior context."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict


@dataclass
class BehaviorContext:
    """Current conditions used by the behavior engine."""

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )

    session_id: str | None = None
    persona_id: str | None = None

    previous_action: str | None = None
    current_topic: str | None = None

    is_active_period: bool = True
    requires_research: bool = False

    network_available: bool = True
    browser_available: bool = True

    activity_count: int = 0
    session_duration_seconds: float = 0.0

    metadata: Dict[str, str] = field(
        default_factory=dict
    )

    def with_action(
        self,
        action: str,
    ) -> "BehaviorContext":
        """Create a context updated with the latest action."""
        return BehaviorContext(
            timestamp=self.timestamp,
            session_id=self.session_id,
            persona_id=self.persona_id,
            previous_action=action,
            current_topic=self.current_topic,
            is_active_period=self.is_active_period,
            requires_research=self.requires_research,
            network_available=self.network_available,
            browser_available=self.browser_available,
            activity_count=self.activity_count + 1,
            session_duration_seconds=(
                self.session_duration_seconds
            ),
            metadata=dict(self.metadata),
        )

    def can_use_network(self) -> bool:
        """Return whether network-dependent behavior is allowed."""
        return (
            self.network_available
            and self.browser_available
        )
