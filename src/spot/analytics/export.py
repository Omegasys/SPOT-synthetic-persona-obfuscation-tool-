from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ExportOptions:
    """Controls analytics export behavior."""

    include_metadata: bool = False
    include_targets: bool = False
    pretty_json: bool = True
    overwrite: bool = False


class AnalyticsExporter:
    """
    Exports aggregate analytics locally.

    Exports deliberately avoid network transmission. Sensitive fields
    such as raw targets can also be excluded by default.
    """

    def __init__(
        self,
        options: ExportOptions | None = None,
    ) -> None:
        self.options = options or ExportOptions()

    def _prepare(
        self,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Remove fields excluded by the export policy."""
        result = dict(data)

        if not self.options.include_metadata:
            result.pop("metadata", None)

        if not self.options.include_targets:
            result.pop("targets", None)
            result.pop("destinations", None)

        return result

    def export_json(
        self,
        data: dict[str, Any],
        path: str | Path,
    ) -> Path:
        """Export analytics as JSON."""
        destination = Path(path).expanduser()

        self._prepare_destination(destination)

        payload = self._prepare(data)

        with destination.open(
            "w",
            encoding="utf-8",
        ) as handle:
            json.dump(
                payload,
                handle,
                indent=2 if self.options.pretty_json else None,
                sort_keys=True,
            )
            handle.write("\n")

        return destination

    def export_csv(
        self,
        records: list[dict[str, Any]],
        path: str | Path,
    ) -> Path:
        """Export sanitized analytics records as CSV."""
        destination = Path(path).expanduser()

        self._prepare_destination(destination)

        sanitized = [
            self._prepare(record)
            for record in records
        ]

        if not sanitized:
            destination.write_text(
                "",
                encoding="utf-8",
            )
            return destination

        fieldnames = sorted(
            {
                key
                for record in sanitized
                for key in record
            }
        )

        with destination.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=fieldnames,
                extrasaction="ignore",
            )

            writer.writeheader()

            for record in sanitized:
                writer.writerow(
                    {
                        key: self._csv_value(value)
                        for key, value in record.items()
                    }
                )

        return destination

    def export_report(
        self,
        report: Any,
        path: str | Path,
    ) -> Path:
        """Export an object exposing to_dict()."""
        if not hasattr(report, "to_dict"):
            raise TypeError(
                "Report must provide a to_dict() method."
            )

        return self.export_json(
            report.to_dict(),
            path,
        )

    def _prepare_destination(
        self,
        destination: Path,
    ) -> None:
        """Validate an export destination."""
        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if destination.exists() and not self.options.overwrite:
            raise FileExistsError(
                f"Export already exists: {destination}"
            )

    @staticmethod
    def _csv_value(value: Any) -> Any:
        """Convert structured values into CSV-safe values."""
        if isinstance(value, (dict, list, tuple)):
            return json.dumps(
                value,
                separators=(",", ":"),
                sort_keys=True,
            )

        return value
