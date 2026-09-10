"""SPOT synthetic persona demographics."""

from **future** import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass
class Demographics:
"""Synthetic demographic information for a persona.

```
All values are intended to describe fictional personas and
should not be derived from private information about real people.
"""

age_range: str = "25-34"
location: str = "synthetic"
language: str = "en"

attributes: Dict[str, Any] = field(default_factory=dict)

def set_attribute(self, name: str, value: Any) -> None:
    """Set a synthetic demographic attribute."""
    self.attributes[name] = value

def get_attribute(
    self,
    name: str,
    default: Any = None,
) -> Any:
    """Return a demographic attribute."""
    return self.attributes.get(name, default)

def to_dict(self) -> Dict[str, Any]:
    """Convert demographics to a dictionary."""
    return {
        "age_range": self.age_range,
        "location": self.location,
        "language": self.language,
        "attributes": dict(self.attributes),
    }

@classmethod
def from_dict(cls, data: Dict[str, Any]) -> "Demographics":
    """Create demographics from a dictionary."""
    return cls(
        age_range=str(
            data.get("age_range", "25-34")
        ),
        location=str(
            data.get("location", "synthetic")
        ),
        language=str(
            data.get("language", "en")
        ),
        attributes=dict(
            data.get("attributes", {})
        ),
    )
```
