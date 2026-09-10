from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .audit_log import AuditLog
from .events import AuditEvent, AuditSeverity
from .redaction import Redactor


@dataclass
class AuditLogger:
    """High-level interface for recording SPOT audit events."""

    audit_log: AuditLog
    redactor: Redactor

    def log(
        self,
        event_type: str,
        message: str,
        *,
        severity: AuditSeverity = AuditSeverity.INFO,
        persona_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditEvent:
        """Create, redact, and store an audit event."""
        event = AuditEvent(
            event_type=event_type,
            severity=severity,
            message=message,
            persona_id=persona_id,
            metadata=metadata or {},
        )

        redacted = self.redactor.redact_event(event)

        self.audit_log.append(redacted)

        return redacted

    def info(
        self,
        event_type: str,
        message: str,
        **kwargs: Any,
    ) -> AuditEvent:
        """Record an informational event."""
        return self.log(
            event_type,
            message,
            severity=AuditSeverity.INFO,
            **kwargs,
        )

    def warning(
        self,
        event_type: str,
        message: str,
        **kwargs: Any,
    ) -> AuditEvent:
        """Record a warning."""
        return self.log(
            event_type,
            message,
            severity=AuditSeverity.WARNING,
            **kwargs,
        )

    def error(
        self,
        event_type: str,
        message: str,
        **kwargs: Any,
    ) -> AuditEvent:
        """Record an error."""
        return self.log(
            event_type,
            message,
            severity=AuditSeverity.ERROR,
            **kwargs,
        )

    def security(
        self,
        event_type: str,
        message: str,
        **kwargs: Any,
    ) -> AuditEvent:
        """Record a security event."""
        return self.log(
            event_type,
            message,
            severity=AuditSeverity.SECURITY,
            **kwargs,
        )

    def emergency(
        self,
        message: str,
        **kwargs: Any,
    ) -> AuditEvent:
        """Record an emergency-stop event."""
        return self.log(
            "emergency_stop",
            message,
            severity=AuditSeverity.EMERGENCY,
            **kwargs,
        )
