from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from time import time
from typing import Any
from uuid import uuid4


class AuditSeverity(str, Enum):
    """Severity levels for audit events."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SECURITY = "security"
    EMERGENCY = "emergency"


class AuditEventType(str, Enum):
    """Common SPOT audit event types."""

    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"

    PERSONA_CREATED = "persona_created"
    PERSONA_ENABLED = "persona_enabled"
    PERSONA_DISABLED = "persona_disabled"
    PERSONA_REMOVED = "persona_removed"

    SESSION_STARTED = "session_started"
    SESSION_STOPPED = "session_stopped"

    ACTIVITY_STARTED = "activity_started"
    ACTIVITY_COMPLETED = "activity_completed"
    ACTIVITY_FAILED = "activity_failed"

    NETWORK_STARTED = "network_started"
    NETWORK_STOPPED = "network_stopped"
    NETWORK_BLOCKED = "network_blocked"

    SAFETY_BLOCK = "safety_block"
    ANOMALY_DETECTED = "anomaly_detected"

    PLUGIN_LOADED = "plugin_loaded"
    PLUGIN_REJECTED = "plugin_rejected"
    PLUGIN_DISABLED = "plugin_disabled"

    EMERGENCY_STOP = "emergency_stop"

    CONFIGURATION_CHANGED = "configuration_changed"
    SECURITY_POLICY_CHANGED = "security_policy_changed"


@dataclass
class AuditEvent:
    """Immutable-style representation of an audit event."""

    event_type: str
    message: str
    severity: AuditSeverity = AuditSeverity.INFO
    persona_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: float = field(default_factory=time)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the event."""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "severity": self.severity.value,
            "persona_id": self.persona_id,
            "message": self.message,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "AuditEvent":
        """Deserialize an audit event."""
        severity = data.get(
            "severity",
            AuditSeverity.INFO.value,
        )

        return cls(
            event_id=str(data["event_id"]),
            timestamp=float(data["timestamp"]),
            event_type=str(data["event_type"]),
            severity=AuditSeverity(severity),
            persona_id=data.get("persona_id"),
            message=str(data["message"]),
            metadata=dict(data.get("metadata", {})),
        )
