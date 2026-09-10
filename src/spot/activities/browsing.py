"""SPOT synthetic browsing activity."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List
from urllib.parse import urlparse


@dataclass
class BrowsingActivity:
    """Prepare bounded synthetic browsing sessions."""

    name: str = "browsing"

    def prepare(
        self,
        urls: Iterable[str] | None = None,
        duration_seconds: int = 300,
        max_pages: int = 10,
        **_: Any,
    ) -> Dict[str, Any]:
        """Prepare a synthetic browsing session."""
        if duration_seconds < 0:
            raise ValueError(
                "duration_seconds cannot be negative."
            )

        if max_pages < 1:
            raise ValueError(
                "max_pages must be at least 1."
            )

        safe_urls: List[str] = []

        for url in urls or []:
            url = str(url)

            parsed = urlparse(url)

            if parsed.scheme not in (
                "http",
                "https",
            ):
                continue

            if not parsed.netloc:
                continue

            safe_urls.append(url)

            if len(safe_urls) >= max_pages:
                break

        return {
            "type": self.name,
            "urls": safe_urls,
            "duration_seconds": duration_seconds,
            "max_pages": max_pages,
            "synthetic": True,
            "requires_execution": True,
        }
