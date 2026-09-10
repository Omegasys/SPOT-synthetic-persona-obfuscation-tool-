"""SPOT synthetic news activity."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List


@dataclass
class NewsActivity:
    """Prepare synthetic news-reading activity."""

    name: str = "news"

    def prepare(
        self,
        topics: Iterable[str] | None = None,
        sources: Iterable[str] | None = None,
        max_items: int = 5,
        **_: Any,
    ) -> Dict[str, Any]:
        """Prepare a bounded synthetic news session."""
        if max_items < 1:
            raise ValueError(
                "max_items must be at least 1."
            )

        selected_topics = [
            str(topic)
            for topic in (topics or [])
            if topic
        ][:max_items]

        selected_sources = [
            str(source)
            for source in (sources or [])
            if source
        ][:max_items]

        return {
            "type": self.name,
            "topics": selected_topics,
            "sources": selected_sources,
            "max_items": max_items,
            "synthetic": True,
            "requires_execution": True,
        }
