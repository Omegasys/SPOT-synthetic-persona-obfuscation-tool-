from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .statistics import CategoryStatistics, NumericStatistics, Statistics


@dataclass
class NetworkReport:
    """Aggregate network-activity report."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    blocked_requests: int = 0

    bytes_sent: int = 0
    bytes_received: int = 0

    routing_modes: CategoryStatistics = field(
        default_factory=CategoryStatistics
    )

    response_times: NumericStatistics = field(
        default_factory=NumericStatistics
    )

    destinations: CategoryStatistics = field(
        default_factory=CategoryStatistics
    )

    @property
    def total_bytes(self) -> int:
        return self.bytes_sent + self.bytes_received

    def success_rate(self) -> float:
        return Statistics.percentage(
            self.successful_requests,
            self.total_requests,
        )

    def blocked_rate(self) -> float:
        return Statistics.percentage(
            self.blocked_requests,
            self.total_requests,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "blocked_requests": self.blocked_requests,
            "success_rate": self.success_rate(),
            "blocked_rate": self.blocked_rate(),
            "bytes_sent": self.bytes_sent,
            "bytes_received": self.bytes_received,
            "total_bytes": self.total_bytes,
            "routing_modes": self.routing_modes.to_dict(),
            "response_times": self.response_times.to_dict(),
            "destinations": self.destinations.to_dict(),
        }


class NetworkReportBuilder:
    """Build aggregate network reports."""

    def build(
        self,
        records: list[dict[str, Any]],
    ) -> NetworkReport:
        """Build a network report from sanitized records."""
        report = NetworkReport()

        modes: list[str] = []
        destinations: list[str] = []
        response_times: list[float] = []

        for record in records:
            report.total_requests += 1

            status = str(
                record.get("status", "")
            ).lower()

            if status in {"success", "ok", "completed"}:
                report.successful_requests += 1
            elif status in {"blocked", "denied"}:
                report.blocked_requests += 1
            elif status in {"failed", "error"}:
                report.failed_requests += 1

            sent = record.get("bytes_sent", 0)
            received = record.get("bytes_received", 0)

            if isinstance(sent, int) and sent >= 0:
                report.bytes_sent += sent

            if isinstance(received, int) and received >= 0:
                report.bytes_received += received

            mode = record.get("routing_mode")
            if mode:
                modes.append(str(mode))

            destination = record.get("destination")
            if destination:
                destinations.append(str(destination))

            response_time = record.get("response_time_seconds")
            if (
                isinstance(response_time, (int, float))
                and response_time >= 0
            ):
                response_times.append(float(response_time))

        report.routing_modes = Statistics.categories(modes)
        report.destinations = Statistics.categories(destinations)
        report.response_times = Statistics.numeric(
            response_times
        )

        return report
