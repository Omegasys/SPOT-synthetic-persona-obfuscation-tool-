"""SPOT synthetic behavior models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class BehaviorTraits:
    """Bounded behavioral characteristics.

    Values range from 0.0 to 1.0.
    """

    activity_level: float = 0.5
    exploration: float = 0.5
    consistency: float = 0.5
    randomness: float = 0.5
    research_depth: float = 0.5
    session_length: float = 0.5
    topic_switching: float = 0.5

    def __post_init__(self) -> None:
        self.activity_level = self._clamp(
            self.activity_level
        )
        self.exploration = self._clamp(
            self.exploration
        )
        self.consistency = self._clamp(
            self.consistency
        )
        self.randomness = self._clamp(
            self.randomness
        )
        self.research_depth = self._clamp(
            self.research_depth
        )
        self.session_length = self._clamp(
            self.session_length
        )
        self.topic_switching = self._clamp(
            self.topic_switching
        )

    @staticmethod
    def _clamp(value: float) -> float:
        """Clamp a trait to 0.0-1.0."""
        return max(0.0, min(1.0, float(value)))


@dataclass
class NoiseBudgetSettings:
    """Limits behavioral randomness."""

    enabled: bool = True

    # Maximum number of randomized decisions per session.
    max_random_decisions: int = 25

    # Maximum fractional deviation introduced by randomization.
    max_variation: float = 0.20


@dataclass
class BehaviorModel:
    """Configuration describing a synthetic behavior profile."""

    name: str = "default"

    traits: BehaviorTraits = field(
        default_factory=BehaviorTraits
    )

    preferred_actions: List[str] = field(
        default_factory=lambda: [
            "search",
            "browse",
            "research",
            "media",
            "idle",
        ]
    )

    action_weights: Dict[str, float] = field(
        default_factory=lambda: {
            "search": 0.25,
            "browse": 0.30,
            "research": 0.15,
            "media": 0.20,
            "idle": 0.10,
        }
    )

    topic_weights: Dict[str, float] = field(
        default_factory=dict
    )

    noise_budget: NoiseBudgetSettings = field(
        default_factory=NoiseBudgetSettings
    )

    def weight_for(self, action: str) -> float:
        """Return the configured weight for an action."""
        return max(
            0.0,
            float(
                self.action_weights.get(
                    action,
                    0.0,
                )
            ),
        )

    def set_weight(
        self,
        action: str,
        weight: float,
    ) -> None:
        """Set a bounded action weight."""
        self.action_weights[action] = max(
            0.0,
            float(weight),
        )

    def add_action(
        self,
        action: str,
        weight: float = 1.0,
    ) -> None:
        """Add an action to the behavior model."""
        if action not in self.preferred_actions:
            self.preferred_actions.append(action)

        self.set_weight(action, weight)
