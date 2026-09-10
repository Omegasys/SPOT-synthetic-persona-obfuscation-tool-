from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .statistics import CategoryStatistics, NumericStatistics, Statistics


@dataclass
class ActivityReport:
    """Aggregate report describing SPOT activity."""

    total_activities: int = 0
    successful_activities: int = 0
    failed_activities: int = 0
    cancelled_activities: int = 0

    activity_types: CategoryStatistics = field(
        default_factory=CategoryStatistics
    )

    durations: NumericStatistics = field(
        default_factory=NumericStatistics
    )

    pages: NumericStatistics = field(
        default_factory=NumericStatistics
    )

    requests: NumericStatistics = field(
        default_factory=NumericStatistics
    )

    def success_rate(self) -> float:
        """Return successful activity percentage."""
        return Statistics.percentage(
            self.successful_activities,
            self.total_activities,
        )

    def failure_rate(self) -> float:
        """Return failed activity percentage."""
        return Statistics.percentage(
            self.failed_activities,
            self.total_activities,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_activities": self.total_activities,
            "successful_activities": self.successful_activities,
            "failed_activities": self.failed_activities,
            "cancelled_activities": self.cancelled_activities,
            "success_rate": self.success_rate(),
            "failure_rate": self.failure_rate(),
            "activity_types": self.activity_types.to_dict(),
            "durations": self.durations.to_dict(),
            "pages": self.pages.to_dict(),
            "requests": self.requests.to_dict(),
        }


class ActivityReportBuilder:
    """Builds activity reports from sanitized activity records."""

    def build(
        self,
        records: list[dict[str, Any]],
    ) -> ActivityReport:
        """Build an aggregate activity report."""
        report = ActivityReport()

        durations: list[float] = []
        pages: list[float] = []
        requests: list[float] = []
        activity_types: list[str] = []

        for record in records:
            report.total_activities += 1

            activity_type = str(
                record.get("activity_type", "unknown")
            )
            activity_types.append(activity_type)

            status = str(
                record.get("status", "unknown")
            ).lower()

            if status in {"success", "completed", "complete"}:
                report.successful_activities += 1
            elif status in {"failed", "failure", "error"}:
                report.failed_activities += 1
            elif status in {"cancelled", "canceled"}:
                report.cancelled_activities += 1

            duration = record.get("duration_seconds")
            if isinstance(duration, (int, float)):
                if duration >= 0:
                    durations.append(float(duration))

            page_count = record.get("pages")
            if isinstance(page_count, (int, float)):
                if page_count >= 0:
                    pages.append(float(page_count))

            request_count = record.get("requests")
            if isinstance(request_count, (int, float)):
                if request_count >= 0:
                    requests.append(float(request_count))

        report.activity_types = Statistics.categories(
            activity_types
        )
        report.durations = Statistics.numeric(durations)
        report.pages = Statistics.numeric(pages)
        report.requests = Statistics.numeric(requests)

        return report
