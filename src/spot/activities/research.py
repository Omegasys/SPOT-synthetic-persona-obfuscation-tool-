"""SPOT synthetic research activity."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List


@dataclass
class ResearchActivity:
    """Prepare structured synthetic research sessions."""

    name: str = "research"

    def prepare(
        self,
        topic: str,
        subtopics: Iterable[str] | None = None,
        depth: int = 2,
        max_steps: int = 10,
        **_: Any,
    ) -> Dict[str, Any]:
        """Prepare a bounded research session."""
        if not topic:
            raise ValueError(
                "Research topic cannot be empty."
            )

        if depth < 1:
            raise ValueError(
                "Research depth must be at least 1."
            )

        if max_steps < 1:
            raise ValueError(
                "max_steps must be at least 1."
            )

        selected_subtopics: List[str] = [
            str(item)
            for item in (subtopics or [])
            if item
        ][:max_steps]

        return {
            "type": self.name,
            "topic": str(topic),
            "subtopics": selected_subtopics,
            "depth": depth,
            "max_steps": max_steps,
            "synthetic": True,
            "requires_execution": True,
        }
