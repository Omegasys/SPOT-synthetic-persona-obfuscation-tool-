"""SPOT synthetic search activity."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List


@dataclass
class SearchActivity:
    """Generate bounded synthetic search activity."""

    name: str = "search"

    def prepare(
        self,
        query: str | None = None,
        topic: str | None = None,
        queries: Iterable[str] | None = None,
        max_queries: int = 5,
        **_: Any,
    ) -> Dict[str, Any]:
        """Prepare synthetic search requests."""
        if max_queries < 1:
            raise ValueError(
                "max_queries must be at least 1."
            )

        generated: List[str] = []

        if query:
            generated.append(str(query))

        if queries:
            generated.extend(
                str(item)
                for item in queries
                if item
            )

        generated = generated[:max_queries]

        return {
            "type": self.name,
            "topic": topic,
            "queries": generated,
            "synthetic": True,
            "requires_execution": True,
        }
