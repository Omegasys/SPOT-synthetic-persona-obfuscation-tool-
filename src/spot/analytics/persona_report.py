from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .statistics import CategoryStatistics, NumericStatistics, Statistics


@dataclass
class PersonaReport:
    """Aggregate analytics for a synthetic persona."""

    persona_id: str
    total_activities: int = 0
    successful_activities: int = 0
    sessions: int = 0
    active_seconds: float = 0.0

    activity_types: CategoryStatistics = field(
        default_factory=CategoryStatistics
    )

    activity_durations: NumericStatistics = field(
        default_factory=NumericStatistics
    )

    topics: CategoryStatistics = field(
        default_factory=CategoryStatistics
    )

    def success_rate(self) -> float:
        return Statistics.percentage(
            self.successful_activities,
            self.total_activities,
        )

    def activity_rate(self) -> float:
        return Statistics.rate(
            self.total_activities,
            self.active_seconds,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "persona_id": self.persona_id,
            "total_activities": self.total_activities,
            "successful_activities": self.successful_activities,
            "success_rate": self.success_rate(),
            "sessions": self.sessions,
            "active_seconds": self.active_seconds,
            "activity_rate": self.activity_rate(),
            "activity_types": self.activity_types.to_dict(),
            "activity_durations": self.activity_durations.to_dict(),
            "topics": self.topics.to_dict(),
        }


class PersonaReportBuilder:
    """Build aggregate reports for individual synthetic personas."""

    def build(
        self,
        persona_id: str,
        records: list[dict[str, Any]],
    ) -> PersonaReport:
        """Build a report for one persona."""
        if not persona_id:
            raise ValueError("persona_id cannot be empty.")

        report = PersonaReport(
            persona_id=persona_id
        )

        activity_types: list[str] = []
        topics: list[str] = []
        durations: list[float] = []

        session_ids: set[str] = set()

        for record in records:
            if record.get("persona_id") != persona_id:
                continue

            report.total_activities += 1

            status = str(
                record.get("status", "")
            ).lower()

            if status in {"success", "completed", "complete"}:
                report.successful_activities += 1

            activity_type = record.get("activity_type")
            if activity_type:
                activity_types.append(str(activity_type))

            topic = record.get("topic")
            if topic:
                topics.append(str(topic))

            duration = record.get("duration_seconds")
            if isinstance(duration, (int, float)) and duration >= 0:
                durations.append(float(duration))

            session_id = record.get("session_id")
            if session_id:
                session_ids.add(str(session_id))

        report.sessions = len(session_ids)
        report.active_seconds = sum(durations)
        report.activity_types = Statistics.categories(
            activity_types
        )
        report.topics = Statistics.categories(topics)
        report.activity_durations = Statistics.numeric(
            durations
        )

        return report
