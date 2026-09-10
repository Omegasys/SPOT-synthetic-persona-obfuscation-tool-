from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .statistics import CategoryStatistics, Statistics


@dataclass
class ConsistencyReport:
    """Measures consistency of a synthetic persona's behavior."""

    persona_id: str

    total_observations: int = 0
    matching_observations: int = 0
    repeated_actions: int = 0
    topic_changes: int = 0

    actions: CategoryStatistics = field(
        default_factory=CategoryStatistics
    )

    topics: CategoryStatistics = field(
        default_factory=CategoryStatistics
    )

    def consistency_score(self) -> float:
        """Return the percentage of matching observations."""
        return Statistics.percentage(
            self.matching_observations,
            self.total_observations,
        )

    def topic_change_rate(self) -> float:
        """Return topic changes per observation."""
        if self.total_observations <= 1:
            return 0.0

        return self.topic_changes / (
            self.total_observations - 1
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "persona_id": self.persona_id,
            "total_observations": self.total_observations,
            "matching_observations": self.matching_observations,
            "repeated_actions": self.repeated_actions,
            "topic_changes": self.topic_changes,
            "consistency_score": self.consistency_score(),
            "topic_change_rate": self.topic_change_rate(),
            "actions": self.actions.to_dict(),
            "topics": self.topics.to_dict(),
        }


class ConsistencyReportBuilder:
    """Build reports describing behavioral consistency."""

    def build(
        self,
        persona_id: str,
        observations: list[dict[str, Any]],
    ) -> ConsistencyReport:
        """Build a consistency report."""
        if not persona_id:
            raise ValueError("persona_id cannot be empty.")

        report = ConsistencyReport(
            persona_id=persona_id
        )

        actions: list[str] = []
        topics: list[str] = []

        previous_action: str | None = None
        previous_topic: str | None = None

        for observation in observations:
            if observation.get("persona_id") != persona_id:
                continue

            report.total_observations += 1

            action = observation.get("action")
            topic = observation.get("topic")

            if action:
                action = str(action)
                actions.append(action)

                if action == previous_action:
                    report.repeated_actions += 1

                previous_action = action

            if topic:
                topic = str(topic)
                topics.append(topic)

                if (
                    previous_topic is not None
                    and topic != previous_topic
                ):
                    report.topic_changes += 1

                previous_topic = topic

            # A caller can provide an explicit consistency result.
            if observation.get("consistent") is True:
                report.matching_observations += 1

        report.actions = Statistics.categories(actions)
        report.topics = Statistics.categories(topics)

        return report
