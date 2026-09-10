from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PersonaRecord:
    """Persisted synthetic persona metadata."""

    id: str
    name: str
    description: str = ""
    enabled: bool = False
    memory_enabled: bool = True
    synthetic_only: bool = True
    created_at: float = 0.0
    updated_at: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled,
            "memory_enabled": self.memory_enabled,
            "synthetic_only": self.synthetic_only,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_row(cls, row: Any) -> "PersonaRecord":
        return cls(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            enabled=bool(row["enabled"]),
            memory_enabled=bool(row["memory_enabled"]),
            synthetic_only=bool(row["synthetic_only"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


@dataclass
class MemoryRecord:
    """Persisted synthetic persona memory."""

    id: str
    persona_id: str
    category: str
    key: str
    value: str
    created_at: float
    updated_at: float


@dataclass
class ActivityRecord:
    """Persisted activity record."""

    id: str
    persona_id: str | None
    activity_type: str
    target: str | None
    status: str
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = 0.0

    def metadata_json(self) -> str:
        """Serialize metadata."""
        return json.dumps(
            self.metadata,
            separators=(",", ":"),
            sort_keys=True,
        )

    @classmethod
    def from_row(cls, row: Any) -> "ActivityRecord":
        return cls(
            id=row["id"],
            persona_id=row["persona_id"],
            activity_type=row["activity_type"],
            target=row["target"],
            status=row["status"],
            metadata=json.loads(row["metadata"] or "{}"),
            created_at=row["created_at"],
        )


@dataclass
class AuditRecord:
    """Persisted security/audit event."""

    id: str
    event_type: str
    severity: str
    message: str
    persona_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = 0.0

    def metadata_json(self) -> str:
        """Serialize audit metadata."""
        return json.dumps(
            self.metadata,
            separators=(",", ":"),
            sort_keys=True,
        )


@dataclass
class SettingRecord:
    """Persisted application setting."""

    key: str
    value: str
    updated_at: float

    def as_json(self) -> Any:
        """Decode a JSON setting value."""
        return json.loads(self.value)
