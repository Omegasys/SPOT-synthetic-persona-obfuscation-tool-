"""SPOT persona model."""

from **future** import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

from .identity import Identity
from .interests import Interests
from .preferences import Preferences

@dataclass
class Persona:
"""Represents one synthetic SPOT persona."""

```
id: str
name: str
description: str = ""

identity: Identity = field(default_factory=Identity)
interests: Interests = field(default_factory=Interests)
preferences: Preferences = field(default_factory=Preferences)

enabled: bool = False

memory_enabled: bool = True
synthetic_only: bool = True

metadata: Dict[str, Any] = field(default_factory=dict)

def enable(self) -> None:
    """Enable the persona."""
    self.enabled = True

def disable(self) -> None:
    """Disable the persona."""
    self.enabled = False

def to_dict(self) -> Dict[str, Any]:
    """Convert the persona to a serializable dictionary."""
    return {
        "id": self.id,
        "name": self.name,
        "description": self.description,
        "identity": self.identity.to_dict(),
        "interests": self.interests.to_dict(),
        "preferences": self.preferences.to_dict(),
        "enabled": self.enabled,
        "memory_enabled": self.memory_enabled,
        "synthetic_only": self.synthetic_only,
        "metadata": dict(self.metadata),
    }

@classmethod
def from_dict(cls, data: Dict[str, Any]) -> "Persona":
    """Create a persona from a dictionary."""
    return cls(
        id=str(data["id"]),
        name=str(data["name"]),
        description=str(data.get("description", "")),
        identity=Identity.from_dict(
            data.get("identity", {})
        ),
        interests=Interests.from_dict(
            data.get("interests", {})
        ),
        preferences=Preferences.from_dict(
            data.get("preferences", {})
        ),
        enabled=bool(data.get("enabled", False)),
        memory_enabled=bool(
            data.get("memory_enabled", True)
        ),
        synthetic_only=bool(
            data.get("synthetic_only", True)
        ),
        metadata=dict(data.get("metadata", {})),
    )
```
