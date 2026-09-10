"""SPOT behavioral noise budget."""

from __future__ import annotations

from typing import Iterable, List

from .context import BehaviorContext
from .model import NoiseBudgetSettings


class NoiseBudget:
    """Limit the amount of behavioral randomization."""

    def __init__(
        self,
        settings: NoiseBudgetSettings | None = None,
    ) -> None:
        self.settings = (
            settings
            or NoiseBudgetSettings()
        )

        self.used = 0

    @property
    def remaining(self) -> int:
        """Return the remaining randomized decisions."""
        return max(
            0,
            self.settings.max_random_decisions
            - self.used,
        )

    def consume(
        self,
        amount: int = 1,
    ) -> bool:
        """Consume part of the noise budget."""
        if amount < 0:
            raise ValueError(
                "Noise budget amount cannot be negative."
            )

        if not self.settings.enabled:
            return False

        if self.used + amount > (
            self.settings.max_random_decisions
        ):
            return False

        self.used += amount
        return True

    def allow(
        self,
        context: BehaviorContext,
        candidates: Iterable[str],
    ) -> List[str]:
        """Return candidates allowed by the noise policy."""
        values = list(candidates)

        if not self.settings.enabled:
            return values

        if self.remaining <= 0:
            if context.previous_action:
                return [context.previous_action]

            return values[:1]

        self.consume()

        return values

    def reset(self) -> None:
        """Reset the noise budget."""
        self.used = 0

    def exhausted(self) -> bool:
        """Return whether the budget has been exhausted."""
        return (
            self.remaining <= 0
        )
