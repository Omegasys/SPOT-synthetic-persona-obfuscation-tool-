from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from .events import AuditEvent


@dataclass
class RedactionPolicy:
    """Defines information that must not enter the audit log."""

    replacement: str = "[REDACTED]"

    sensitive_keys: set[str] = field(
        default_factory=lambda: {
            "password",
            "passphrase",
            "token",
            "access_token",
            "refresh_token",
            "api_key",
            "secret",
            "private_key",
            "credential",
            "credentials",
            "cookie",
            "session_cookie",
            "authorization",
            "auth",
            "personal_data",
            "real_name",
            "email",
            "phone",
            "address",
        }
    )

    sensitive_patterns: tuple[str, ...] = (
        r"(?i)bearer\s+[A-Za-z0-9._~+/=-]+",
        r"(?i)basic\s+[A-Za-z0-9+/=]+",
        r"(?i)(api[_-]?key|token|secret)\s*[:=]\s*\S+",
        r"(?i)password\s*[:=]\s*\S+",
    )


class Redactor:
    """Redacts sensitive values before they enter audit storage."""

    def __init__(
        self,
        policy: RedactionPolicy | None = None,
    ) -> None:
        self.policy = policy or RedactionPolicy()

        self._patterns = [
            re.compile(pattern)
            for pattern in self.policy.sensitive_patterns
        ]

    def redact_text(self, value: str) -> str:
        """Redact known sensitive patterns from text."""
        result = value

        for pattern in self._patterns:
            result = pattern.sub(
                self.policy.replacement,
                result,
            )

        return result

    def redact_value(
        self,
        key: str | None,
        value: Any,
    ) -> Any:
        """Recursively redact a value."""
        normalized_key = (
            key.lower().replace("-", "_")
            if key
            else ""
        )

        if normalized_key in self.policy.sensitive_keys:
            return self.policy.replacement

        if isinstance(value, str):
            return self.redact_text(value)

        if isinstance(value, dict):
            return {
                str(child_key): self.redact_value(
                    str(child_key),
                    child_value,
                )
                for child_key, child_value in value.items()
            }

        if isinstance(value, list):
            return [
                self.redact_value(None, item)
                for item in value
            ]

        if isinstance(value, tuple):
            return tuple(
                self.redact_value(None, item)
                for item in value
            )

        return value

    def redact_metadata(
        self,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        """Redact a metadata dictionary."""
        return self.redact_value(
            None,
            metadata,
        )

    def redact_event(
        self,
        event: AuditEvent,
    ) -> AuditEvent:
        """Return a redacted copy of an audit event."""
        return AuditEvent(
            event_id=event.event_id,
            timestamp=event.timestamp,
            event_type=self.redact_text(event.event_type),
            severity=event.severity,
            persona_id=self.redact_text(event.persona_id)
            if event.persona_id
            else None,
            message=self.redact_text(event.message),
            metadata=self.redact_metadata(event.metadata),
        )
