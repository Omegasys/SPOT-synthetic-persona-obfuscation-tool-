"""SPOT synthetic behavior consistency controls."""

from __future__ import annotations

from collections import deque
from typing import Deque, List

from .decision import BehaviorDecision
from .model import BehaviorModel


class ConsistencyController:
    """Keep synthetic behavior coherent over time."""

    def __init__(
        self,
        model: BehaviorModel,
        history_size: int = 10,
    ) -> None:
        self.model = model
        self.history: Deque[str] = deque(
            maxlen=max(1, history_size)
        )

    def apply(
        self,
        decision: BehaviorDecision,
    ) -> BehaviorDecision:
        """Apply consistency rules to a decision."""
        if not self.history:
            return decision

        previous = self.history[-1]

        if (
            previous == decision.action
            and self.model.traits.consistency > 0.8
        ):
            decision.confidence = min(
                1.0,
                decision.confidence + 0.05,
            )

        return decision

    def record(
        self,
        decision: BehaviorDecision,
    ) -> None:
        """Record a completed decision."""
        self.history.append(decision.action)

    def recent_actions(self) -> List[str]:
        """Return recent actions."""
        return list(self.history)

    def reset(self) -> None:
        """Clear behavioral history."""
        self.history.clear()

    def repeated_action_count(
        self,
        action: str,
    ) -> int:
        """Count recent uses of an action."""
        return sum(
            1
            for item in self.history
            if item == action
        )
