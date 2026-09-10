"""SPOT synthetic behavior decisions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable

from .context import BehaviorContext
from .model import BehaviorModel
from .probability import ProbabilityModel


@dataclass
class BehaviorDecision:
    """A single synthetic behavior decision."""

    action: str
    confidence: float = 0.5
    reason: str = ""
    parameters: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert the decision to a dictionary."""
        return {
            "action": self.action,
            "confidence": self.confidence,
            "reason": self.reason,
            "parameters": dict(self.parameters),
        }


class DecisionEngine:
    """Select actions from a behavior model."""

    def __init__(
        self,
        model: BehaviorModel,
        seed: int | None = None,
    ) -> None:
        self.model = model
        self.probability = ProbabilityModel(seed=seed)

    def choose(
        self,
        context: BehaviorContext,
        candidates: Iterable[str],
    ) -> BehaviorDecision:
        """Choose a weighted synthetic action."""
        candidate_list = list(candidates)

        if not candidate_list:
            return BehaviorDecision(
                action="idle",
                confidence=1.0,
                reason="No candidate actions available.",
            )

        weights = {
            action: self._score_action(
                action,
                context,
            )
            for action in candidate_list
        }

        action = self.probability.choose(
            weights
        )

        total = sum(weights.values())
        confidence = (
            weights.get(action, 0.0) / total
            if total > 0
            else 0.0
        )

        return BehaviorDecision(
            action=action,
            confidence=confidence,
            reason=(
                "Selected from synthetic behavioral "
                "preferences and current context."
            ),
        )

    def _score_action(
        self,
        action: str,
        context: BehaviorContext,
    ) -> float:
        """Calculate an action score."""
        base = self.model.weight_for(action)

        if base <= 0:
            return 0.0

        score = base

        if context.is_active_period:
            score *= 1.0 + (
                self.model.traits.activity_level * 0.5
            )

        if context.requires_research:
            if action == "research":
                score *= 1.0 + (
                    self.model.traits.research_depth
                )
            elif action == "search":
                score *= 1.0 + (
                    self.model.traits.research_depth * 0.5
                )

        if context.previous_action == action:
            score *= (
                1.0
                + self.model.traits.consistency * 0.5
            )

        if (
            context.previous_action
            and context.previous_action != action
        ):
            score *= (
                1.0
                + self.model.traits.topic_switching * 0.25
            )

        return max(0.0, score)
