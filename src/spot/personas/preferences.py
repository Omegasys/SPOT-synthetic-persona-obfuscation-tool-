"""SPOT persona preferences."""

from **future** import annotations

from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class Preferences:
"""Content and activity preferences for a persona."""

```
content_types: List[str] = field(default_factory=list)
topics: List[str] = field(default_factory=list)
languages: List[str] = field(
    default_factory=lambda: ["en"]
)

def add_content_type(self, content_type: str) -> None:
    """Add a preferred content type."""
    self._add_unique(
        self.content_types,
        content_type,
    )

def add_topic(self, topic: str) -> None:
    """Add a preferred topic."""
    self._add_unique(self.topics, topic)

def add_language(self, language: str) -> None:
    """Add a preferred language."""
    self._add_unique(self.languages, language)

def remove_topic(self, topic: str) -> None:
    """Remove a topic."""
    if topic in self.topics:
        self.topics.remove(topic)

def remove_content_type(self, content_type: str) -> None:
    """Remove a content type."""
    if content_type in self.content_types:
        self.content_types.remove(content_type)

def to_dict(self) -> Dict[str, List[str]]:
    """Convert preferences to a dictionary."""
    return {
        "content_types": list(self.content_types),
        "topics": list(self.topics),
        "languages": list(self.languages),
    }

@classmethod
def from_dict(cls, data: Dict[str, object]) -> "Preferences":
    """Create preferences from a dictionary."""
    return cls(
        content_types=list(
            data.get("content_types", [])
        ),
        topics=list(
            data.get("topics", [])
        ),
        languages=list(
            data.get("languages", ["en"])
        ),
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
