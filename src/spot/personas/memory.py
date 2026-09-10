"""SPOT synthetic persona memory."""

from **future** import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List

@dataclass
class MemoryEntry:
"""A single synthetic memory entry."""

```
key: str
value: str
category: str = "general"
created_at: datetime = field(
    default_factory=lambda: datetime.now(timezone.utc)
)
```

class SyntheticMemory:
"""Stores non-sensitive synthetic persona memories."""

```
def __init__(
    self,
    enabled: bool = True,
    max_entries: int = 100,
) -> None:
    self.enabled = enabled
    self.max_entries = max_entries
    self._entries: Dict[str, MemoryEntry] = {}

def remember(
    self,
    key: str,
    value: str,
    category: str = "general",
) -> None:
    """Store a synthetic memory entry."""
    if not self.enabled:
        return

    self._entries[key] = MemoryEntry(
        key=key,
        value=value,
        category=category,
    )

    self._enforce_limit()

def recall(self, key: str) -> str | None:
    """Recall a memory value."""
    if not self.enabled:
        return None

    entry = self._entries.get(key)

    if entry is None:
        return None

    return entry.value

def forget(self, key: str) -> None:
    """Delete a memory entry."""
    self._entries.pop(key, None)

def clear(self) -> None:
    """Delete all synthetic memories."""
    self._entries.clear()

def entries(self) -> List[MemoryEntry]:
    """Return stored memory entries."""
    return list(self._entries.values())

def _enforce_limit(self) -> None:
    """Keep memory within the configured limit."""
    while len(self._entries) > self.max_entries:
        oldest_key = next(iter(self._entries))
        del self._entries[oldest_key]
```
