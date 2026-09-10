"""SPOT persona interests."""

from **future** import annotations

from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class Interests:
"""Interests associated with a synthetic persona."""

```
primary: List[str] = field(default_factory=list)
secondary: List[str] = field(default_factory=list)

def add_primary(self, interest: str) -> None:
    """Add a primary interest."""
    self._add_unique(self.primary, interest)

def add_secondary(self, interest: str) -> None:
    """Add a secondary interest."""
    self._add_unique(self.secondary, interest)

def remove(self, interest: str) -> None:
    """Remove an interest from either category."""
    if interest in self.primary:
        self.primary.remove(interest)

    if interest in self.secondary:
        self.secondary.remove(interest)

def all(self) -> List[str]:
    """Return all interests."""
    return list(dict.fromkeys(
        self.primary + self.secondary
    ))

def contains(self, interest: str) -> bool:
    """Check whether an interest exists."""
    return interest in self.primary or interest in self.secondary

def to_dict(self) -> Dict[str, List[str]]:
    """Convert interests to a dictionary."""
    return {
        "primary": list(self.primary),
        "secondary": list(self.secondary),
    }

@classmethod
def from_dict(cls, data: Dict[str, object]) -> "Interests":
    """Create interests from a dictionary."""
    return cls(
        primary=list(data.get("primary", [])),
        secondary=list(data.get("secondary", [])),
    )

@staticmethod
def _add_unique(
    collection: List[str],
    value: str,
) -> None:
    """Add a value if it is not already present."""
    if value not in collection:
        collection.append(value)
```
