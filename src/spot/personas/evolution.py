"""SPOT synthetic persona evolution."""

from **future** import annotations

from dataclasses import dataclass, field
from typing import Dict

@dataclass
class EvolutionSettings:
"""Controls how a synthetic persona may change over time."""

```
enabled: bool = True

# Maximum amount of change allowed during one update.
max_change: float = 0.10

# Keep persona behavior reasonably consistent.
preserve_identity: bool = True
```

@dataclass
class EvolutionState:
"""Current synthetic evolution state."""

```
activity_count: int = 0
session_count: int = 0

traits: Dict[str, float] = field(
    default_factory=dict
)
```

class Evolution:
"""Manages controlled changes to synthetic persona behavior."""

```
def __init__(
    self,
    settings: EvolutionSettings | None = None,
) -> None:
    self.settings = settings or EvolutionSettings()
    self.state = EvolutionState()

def record_activity(self) -> None:
    """Record one completed synthetic activity."""
    self.state.activity_count += 1

def record_session(self) -> None:
    """Record one completed synthetic session."""
    self.state.session_count += 1

def set_trait(
    self,
    name: str,
    value: float,
) -> None:
    """Set a bounded synthetic behavioral trait."""
    self.state.traits[name] = self._clamp(value)

def adjust_trait(
    self,
    name: str,
    change: float,
) -> float:
    """Adjust a trait by a limited amount."""
    if not self.settings.enabled:
        return self.state.traits.get(name, 0.5)

    change = max(
        -self.settings.max_change,
        min(self.settings.max_change, change),
    )

    current = self.state.traits.get(name, 0.5)
    updated = self._clamp(current + change)

    self.state.traits[name] = updated

    return updated

def get_trait(
    self,
    name: str,
    default: float = 0.5,
) -> float:
    """Return a synthetic behavioral trait."""
    return self.state.traits.get(name, default)

@staticmethod
def _clamp(value: float) -> float:
    """Clamp a trait to the 0.0-1.0 range."""
    return max(0.0, min(1.0, float(value)))
```
