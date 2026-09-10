"""SPOT synthetic persona routines."""

from **future** import annotations

from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class Routine:
"""Represents a preferred synthetic activity period."""

```
day: str
preferred_time: str
activity_types: List[str] = field(default_factory=list)
```

@dataclass
class Routines:
"""Collection of routines for a synthetic persona."""

```
enabled: bool = True
routines: List[Routine] = field(
    default_factory=list
)

def add(
    self,
    day: str,
    preferred_time: str,
    activity_types: List[str] | None = None,
) -> None:
    """Add a routine."""
    self.routines.append(
        Routine(
            day=day,
            preferred_time=preferred_time,
            activity_types=activity_types or [],
        )
    )

def remove(self, index: int) -> None:
    """Remove a routine by index."""
    if index < 0 or index >= len(self.routines):
        raise IndexError("Routine index out of range.")

    self.routines.pop(index)

def clear(self) -> None:
    """Remove all routines."""
    self.routines.clear()

def for_day(self, day: str) -> List[Routine]:
    """Return routines matching a day."""
    return [
        routine
        for routine in self.routines
        if routine.day.lower() == day.lower()
    ]

def to_dict(self) -> Dict[str, object]:
    """Convert routines to a dictionary."""
    return {
        "enabled": self.enabled,
        "routines": [
            {
                "day": routine.day,
                "preferred_time": routine.preferred_time,
                "activity_types": list(
                    routine.activity_types
                ),
            }
            for routine in self.routines
        ],
    }

@classmethod
def from_dict(
    cls,
    data: Dict[str, object],
) -> "Routines":
    """Create routines from a dictionary."""
    routines = cls(
        enabled=bool(data.get("enabled", True))
    )

    for item in data.get("routines", []):
        if not isinstance(item, dict):
            continue

        routines.add(
            day=str(item.get("day", "any")),
            preferred_time=str(
                item.get("preferred_time", "any")
            ),
            activity_types=list(
                item.get("activity_types", [])
            ),
        )

    return routines
```
