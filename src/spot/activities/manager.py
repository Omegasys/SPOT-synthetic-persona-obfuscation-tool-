"""SPOT synthetic activity manager."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .browsing import BrowsingActivity
from .dns import DNSActivity
from .media import MediaActivity
from .news import NewsActivity
from .research import ResearchActivity
from .search import SearchActivity
from .shopping import ShoppingActivity


@dataclass
class ActivityRequest:
    """A request for one synthetic activity."""

    activity_type: str
    parameters: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class ActivityResult:
    """Result returned by an activity module."""

    activity_type: str
    success: bool
    data: Dict[str, Any] = field(
        default_factory=dict
    )
    error: str | None = None


class ActivityManager:
    """Manage available synthetic activity types."""

    def __init__(self) -> None:
        self.activities = {
            "search": SearchActivity(),
            "browsing": BrowsingActivity(),
            "news": NewsActivity(),
            "media": MediaActivity(),
            "shopping": ShoppingActivity(),
            "research": ResearchActivity(),
            "dns": DNSActivity(),
        }

    def available(self) -> List[str]:
        """Return available activity types."""
        return sorted(self.activities.keys())

    def get(self, activity_type: str):
        """Return an activity implementation."""
        activity = self.activities.get(activity_type)

        if activity is None:
            raise KeyError(
                f"Unknown activity type: {activity_type}"
            )

        return activity

    def execute(
        self,
        request: ActivityRequest,
    ) -> ActivityResult:
        """Prepare a synthetic activity."""
        try:
            activity = self.get(
                request.activity_type
            )

            data = activity.prepare(
                **request.parameters
            )

            return ActivityResult(
                activity_type=request.activity_type,
                success=True,
                data=data,
            )

        except Exception as exc:
            return ActivityResult(
                activity_type=request.activity_type,
                success=False,
                error=str(exc),
            )
