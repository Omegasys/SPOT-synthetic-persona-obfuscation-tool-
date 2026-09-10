"""SPOT synthetic media activity."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List


@dataclass
class MediaActivity:
    """Prepare synthetic media consumption activity."""

    name: str = "media"

    ALLOWED_TYPES = {
        "video",
        "audio",
        "music",
        "podcast",
        "image",
        "stream",
    }

    def prepare(
        self,
        media_type: str = "video",
        items: Iterable[str] | None = None,
        duration_seconds: int = 300,
        max_items: int = 5,
        **_: Any,
    ) -> Dict[str, Any]:
        """Prepare a bounded synthetic media session."""
        media_type = media_type.lower()

        if media_type not in self.ALLOWED_TYPES:
            raise ValueError(
                f"Unsupported media type: {media_type}"
            )

        if duration_seconds < 0:
            raise ValueError(
                "duration_seconds cannot be negative."
            )

        if max_items < 1:
            raise ValueError(
                "max_items must be at least 1."
            )

        selected = [
            str(item)
            for item in (items or [])
            if item
        ][:max_items]

        return {
            "type": self.name,
            "media_type": media_type,
            "items": selected,
            "duration_seconds": duration_seconds,
            "max_items": max_items,
            "synthetic": True,
            "requires_execution": True,
        }
