"""SPOT synthetic behavior engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List

from .consistency import ConsistencyController
from .context import BehaviorContext
from .decision import BehaviorDecision, DecisionEngine
from .model import BehaviorModel
from .noise_budget import NoiseBudget
from .randomization import Randomization


@dataclass
class BehaviorResult:
    """Result produced by the behavior engine."""

    decision: BehaviorDecision
    metadata: Dict[str, Any]


class BehaviorEngine:
    """Generate bounded synthetic behavior decisions."""

    def __init__(
        self,
        model: BehaviorModel | None = None,
        seed: int | None = None,
    ) -> None:
        self.model = model or BehaviorModel()
        self.decision_engine = DecisionEngine(self.model, seed=seed)
        self.consistency = ConsistencyController(self.model)
        self.randomization = Randomization(seed=seed)
        self.noise_budget = NoiseBudget(
            self.model.noise_budget
        )

    def decide(
        self,
        context: BehaviorContext | None = None,
        candidates: Iterable[str] | None = None,
    ) -> BehaviorResult:
        """Choose the next synthetic behavior."""
        context = context or BehaviorContext()

        candidate_list = list(
            candidates
            or self.model.preferred_actions
        )

        if not candidate_list:
            candidate_list = ["idle"]

        allowed = self.noise_budget.allow(
            context,
            candidate_list,
        )

        if not allowed:
            allowed = ["idle"]

        decision = self.decision_engine.choose(
            context=context,
            candidates=allowed,
        )

        decision = self.consistency.apply(decision)

        return BehaviorResult(
            decision=decision,
            metadata={
                "noise_remaining": (
                    self.noise_budget.remaining
                ),
                "behavior_profile": self.model.name,
            },
        )

    def record(
        self,
        decision: BehaviorDecision,
    ) -> None:
        """Record a completed synthetic decision."""
        self.consistency.record(decision)

    def reset(self) -> None:
        """Reset transient behavioral state."""
        self.consistency.reset()
        self.noise_budget.reset()
