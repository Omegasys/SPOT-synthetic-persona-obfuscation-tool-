"""SPOT synthetic persona identity."""

from **future** import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass
class Identity:
"""Synthetic identity information for a persona.

```
Identity data must remain synthetic and should never be
populated from a real person's private information.
"""

age_range: str = "25-34"
location: str = "synthetic"
language: str = "en"

attributes: Dict[str, Any] = field(default_factory=dict)

def to_dict(self) -> Dict[str, Any]:
    """Convert identity data to a dictionary."""
    return {
        "age_range": self.age_range,
        "location": self.location,
        "language": self.language,
        "attributes": dict(self.attributes),
    }

@classmethod
def from_dict(cls, data: Dict[str, Any]) -> "Identity":
    """Create an identity from a dictionary."""
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
