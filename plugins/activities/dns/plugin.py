from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Optional
import ipaddress
import re

from spot.plugins.interface import PluginMetadata, SPOTPlugin


class DNSRecordType(str, Enum):
    """Supported DNS record types."""

    A = "A"
    AAAA = "AAAA"
    CNAME = "CNAME"
    MX = "MX"
    NS = "NS"
    TXT = "TXT"


@dataclass
class DNSRequest:
    """A bounded synthetic DNS request."""

    domain: str
    record_type: DNSRecordType = DNSRecordType.A
    persona_id: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.domain or not self.domain.strip():
            raise ValueError("DNS domain cannot be empty.")

        if len(self.domain) > 253:
            raise ValueError("DNS domain is too long.")

        if not _valid_domain(self.domain):
            raise ValueError("Invalid DNS domain.")

        if self.record_type not in DNSRecordType:
            raise ValueError("Unsupported DNS record type.")


@dataclass
class DNSResult:
    """Provider-neutral DNS activity result."""

    success: bool
    request: DNSRequest
    answers: list[str] = field(default_factory=list)
    error: Optional[str] = None


def _valid_domain(domain: str) -> bool:
    """Perform conservative DNS domain validation."""

    domain = domain.strip().rstrip(".")

    if not domain:
        return False

    if len(domain) > 253:
        return False

    labels = domain.split(".")

    if any(not label for label in labels):
        return False

    label_pattern = re.compile(
        r"^[A-Za-z0-9]"
        r"(?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$"
    )

    return all(
        label_pattern.fullmatch(label) is not None
        for label in labels
    )


class DNSPlugin(SPOTPlugin):
    """
    SPOT synthetic DNS activity plugin.

    This plugin prepares DNS requests but does not resolve them directly.
    Actual DNS resolution belongs to SPOT's network layer.
    """

    metadata = PluginMetadata(
        id="activity-dns",
        name="DNS Activity Plugin",
        version="0.1.0",
        description=(
            "Provides bounded, policy-controlled synthetic DNS activity."
        ),
    )

    def __init__(
        self,
        max_queries: int = 100,
        allowed_record_types: Optional[set[DNSRecordType]] = None,
        block_private_targets: bool = True,
    ) -> None:
        self.max_queries = max_queries

        self.allowed_record_types = (
            allowed_record_types
            if allowed_record_types is not None
            else set(DNSRecordType)
        )

        self.block_private_targets = block_private_targets

        self._initialized = False
        self._running = False
        self._query_count = 0

    def initialize(self, context: Any) -> bool:
        """Initialize the plugin with an SPOT plugin context."""
        self.context = context
        self._initialized = True
        return True

    def start(self) -> bool:
        """Start the plugin."""
        if not self._initialized:
            return False

        self._running = True
        return True

    def stop(self) -> bool:
        """Stop the plugin."""
        self._running = False
        return True

    def health_check(self) -> bool:
        """Return whether the plugin is operational."""
        return self._initialized and self._running

    def reset(self) -> None:
        """Reset the local query counter."""
        self._query_count = 0

    def prepare_query(
        self,
        domain: str,
        record_type: DNSRecordType | str = DNSRecordType.A,
        persona_id: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> DNSRequest:
        """Prepare a bounded DNS query."""

        if not isinstance(domain, str):
            raise TypeError("domain must be a string.")

        domain = domain.strip().rstrip(".")

        if not domain:
            raise ValueError("DNS domain cannot be empty.")

        if not _valid_domain(domain):
            raise ValueError("Invalid DNS domain.")

        if isinstance(record_type, str):
            try:
                record_type = DNSRecordType(record_type.upper())
            except ValueError as exc:
                raise ValueError(
                    f"Unsupported DNS record type: {record_type}"
                ) from exc

        if record_type not in self.allowed_record_types:
            raise ValueError(
                f"DNS record type is not allowed: {record_type.value}"
            )

        request = DNSRequest(
            domain=domain,
            record_type=record_type,
            persona_id=persona_id,
            metadata=dict(metadata or {}),
        )

        request.validate()

        return request

    def execute(
        self,
        domain: str,
        record_type: DNSRecordType | str = DNSRecordType.A,
        persona_id: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> DNSResult:
        """
        Prepare a DNS activity request.

        Actual DNS resolution is intentionally delegated to SPOT's
        network layer.
        """

        try:
            request = self.prepare_query(
                domain=domain,
                record_type=record_type,
                persona_id=persona_id,
                metadata=metadata,
            )
        except (TypeError, ValueError) as exc:
            fallback_type = (
                DNSRecordType.A
                if not isinstance(record_type, DNSRecordType)
                else record_type
            )

            return DNSResult(
                success=False,
                request=DNSRequest(
                    domain=str(domain),
                    record_type=fallback_type,
                ),
                error=str(exc),
            )

        if not self._running:
            return DNSResult(
                success=False,
                request=request,
                error="DNS plugin is not running.",
            )

        if self._query_count >= self.max_queries:
            return DNSResult(
                success=False,
                request=request,
                error="DNS query limit has been reached.",
            )

        self._query_count += 1

        return DNSResult(
            success=True,
            request=request,
            answers=[],
        )

    def can_use_destination(self, destination: str) -> bool:
        """
        Determine whether an IP destination is acceptable under the
        plugin's conservative private-address policy.
        """

        if not self.block_private_targets:
            return True

        try:
            address = ipaddress.ip_address(destination)
        except ValueError:
            return False

        return not (
            address.is_private
            or address.is_loopback
            or address.is_link_local
            or address.is_multicast
            or address.is_reserved
            or address.is_unspecified
        )


PLUGIN = DNSPlugin()
