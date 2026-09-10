"""SPOT scheduler concurrency controls."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class ConcurrencyPolicy:
    """Limits for simultaneously running scheduled work."""

    max_concurrent: int = 3

    max_per_persona: int = 1

    enabled: bool = True


class ConcurrencyController:
    """Enforce scheduler concurrency limits."""

    def __init__(
        self,
        policy: ConcurrencyPolicy | None = None,
    ) -> None:
        self.policy = (
            policy
            or ConcurrencyPolicy()
        )

        self.active_count = 0

        self.persona_counts: Dict[
            str,
            int,
        ] = {}

    def can_start(
        self,
        persona_id: str | None = None,
    ) -> bool:
        """Check whether another job may start."""
        if not self.policy.enabled:
            return True

        if (
            self.active_count
            >= self.policy.max_concurrent
        ):
            return False

        if persona_id is not None:
            count = self.persona_counts.get(
                persona_id,
                0,
            )

            if count >= self.policy.max_per_persona:
                return False

        return True

    def start(
        self,
        persona_id: str | None = None,
    ) -> bool:
        """Reserve a concurrency slot."""
        if not self.can_start(persona_id):
            return False

        self.active_count += 1

        if persona_id is not None:
            self.persona_counts[persona_id] = (
                self.persona_counts.get(
                    persona_id,
                    0,
                )
                + 1
            )

        return True

    def finish(
        self,
        persona_id: str | None = None,
    ) -> None:
        """Release a concurrency slot."""
        if self.active_count > 0:
            self.active_count -= 1

        if persona_id is not None:
            count = self.persona_counts.get(
                persona_id,
                0,
            )

            if count <= 1:
                self.persona_counts.pop(
                    persona_id,
                    None,
                )
            else:
                self.persona_counts[
                    persona_id
                ] = count - 1

    def reset(self) -> None:
        """Clear all concurrency state."""
        self.active_count = 0
        self.persona_counts.clear()

    def available_slots(self) -> int:
        """Return available global concurrency slots."""
        if not self.policy.enabled:
            return self.policy.max_concurrent

        return max(
            0,
            self.policy.max_concurrent
            - self.active_count,
        )

    def active_for_persona(
        self,
        persona_id: str,
    ) -> int:
        """Return active jobs for a persona."""
        return self.persona_counts.get(
            persona_id,
            0,
        )
