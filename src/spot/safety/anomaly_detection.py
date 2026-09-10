from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from time import time


@dataclass
class AnomalyThresholds:
    """Thresholds used for conservative anomaly detection."""

    max_actions_per_window: int = 30
    max_targets_per_window: int = 20
    max_repeated_target_count: int = 10
    window_seconds: int = 60

    def validate(self) -> None:
        """Validate anomaly thresholds."""
        if self.max_actions_per_window < 1:
            raise ValueError("max_actions_per_window must be positive.")

        if self.max_targets_per_window < 1:
            raise ValueError("max_targets_per_window must be positive.")

        if self.max_repeated_target_count < 1:
            raise ValueError("max_repeated_target_count must be positive.")

        if self.window_seconds < 1:
            raise ValueError("window_seconds must be positive.")


@dataclass
class ActivityObservation:
    """A minimal observation used for anomaly analysis."""

    timestamp: float
    action: str
    target: str | None = None


@dataclass
class AnomalyResult:
    """Result of an anomaly evaluation."""

    anomalous: bool
    reasons: list[str] = field(default_factory=list)
    score: float = 0.0


class AnomalyDetector:
    """
    Detects unusual activity patterns.

    This is intentionally defensive. It does not attempt to identify
    real people, defeat anti-abuse systems, or optimize evasion.
    """

    def __init__(
        self,
        thresholds: AnomalyThresholds | None = None,
        history_size: int = 500,
    ) -> None:
        if history_size < 1:
            raise ValueError("history_size must be positive.")

        self.thresholds = thresholds or AnomalyThresholds()
        self.thresholds.validate()

        self._history: dict[str, deque[ActivityObservation]] = {}
        self._history_size = history_size

    def _scope_history(self, scope: str) -> deque[ActivityObservation]:
        if not scope:
            raise ValueError("scope cannot be empty.")

        if scope not in self._history:
            self._history[scope] = deque(maxlen=self._history_size)

        return self._history[scope]

    def record(
        self,
        scope: str,
        action: str,
        target: str | None = None,
    ) -> AnomalyResult:
        """Record an observation and immediately evaluate it."""
        if not action:
            raise ValueError("action cannot be empty.")

        history = self._scope_history(scope)

        history.append(
            ActivityObservation(
                timestamp=time(),
                action=action,
                target=target,
            )
        )

        return self.evaluate(scope)

    def evaluate(self, scope: str) -> AnomalyResult:
        """Evaluate recent activity for suspicious bursts or repetition."""
        now = time()
        history = self._scope_history(scope)
        window = self.thresholds.window_seconds

        recent = [
            observation
            for observation in history
            if now - observation.timestamp <= window
        ]

        reasons: list[str] = []
        score = 0.0

        if len(recent) > self.thresholds.max_actions_per_window:
            reasons.append("activity_rate_exceeded")
            score += 1.0

        targets = [
            observation.target
            for observation in recent
            if observation.target
        ]

        unique_targets = set(targets)

        if len(unique_targets) > self.thresholds.max_targets_per_window:
            reasons.append("target_diversity_exceeded")
            score += 1.0

        repeated_targets = {
            target
            for target in unique_targets
            if targets.count(target)
            > self.thresholds.max_repeated_target_count
        }

        if repeated_targets:
            reasons.append("repeated_target_pattern")
            score += 1.0

        return AnomalyResult(
            anomalous=bool(reasons),
            reasons=reasons,
            score=score,
        )

    def recent(
        self,
        scope: str,
        limit: int = 20,
    ) -> list[ActivityObservation]:
        """Return recent observations without exposing older history."""
        if limit < 1:
            raise ValueError("limit must be positive.")

        history = self._scope_history(scope)
        return list(history)[-limit:]

    def reset(self, scope: str | None = None) -> None:
        """Clear observations."""
        if scope is None:
            self._history.clear()
            return

        self._history.pop(scope, None)

    def summary(self, scope: str) -> dict[str, object]:
        """Return a compact anomaly summary."""
        result = self.evaluate(scope)

        return {
            "anomalous": result.anomalous,
            "score": result.score,
            "reasons": list(result.reasons),
            "recent_observations": len(self._scope_history(scope)),
        }
