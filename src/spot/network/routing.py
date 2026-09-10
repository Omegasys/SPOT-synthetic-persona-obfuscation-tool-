"""SPOT network routing policies."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import ipaddress
from typing import List


class NetworkMode(str, Enum):
    """Supported SPOT network routing modes."""

    DISABLED = "disabled"
    DIRECT = "direct"
    PROXY = "proxy"
    TOR = "tor"
    WHONIX = "whonix"


@dataclass
class RoutingPolicy:
    """Security policy controlling network routing."""

    mode: NetworkMode = NetworkMode.WHONIX

    fail_closed: bool = True
    fallback_enabled: bool = False

    block_private_addresses: bool = True
    block_loopback: bool = True
    block_link_local: bool = True

    allowed_domains: List[str] = field(
        default_factory=list
    )

    blocked_domains: List[str] = field(
        default_factory=list
    )

    max_requests: int = 100
    max_bandwidth_mb: int = 100

    def validate(self) -> None:
        """Validate routing policy."""
        if self.max_requests < 1:
            raise ValueError(
                "max_requests must be at least 1."
            )

        if self.max_bandwidth_mb < 1:
            raise ValueError(
                "max_bandwidth_mb must be at least 1."
            )

        if self.fail_closed and self.fallback_enabled:
            raise ValueError(
                "Fallback routing cannot be enabled "
                "with fail-closed mode."
            )

        if (
            self.mode == NetworkMode.WHONIX
            and self.fallback_enabled
        ):
            raise ValueError(
                "Whonix routing cannot use automatic fallback."
            )

    def destination_allowed(
        self,
        host: str,
    ) -> bool:
        """Check whether a hostname or IP is allowed."""
        host = host.strip().lower().rstrip(".")

        if not host:
            return False

        if self._is_blocked_ip(host):
            return False

        if self.blocked_domains and self._domain_matches(
            host,
            self.blocked_domains,
        ):
            return False

        if self.allowed_domains:
            return self._domain_matches(
                host,
                self.allowed_domains,
            )

        return True

    def _is_blocked_ip(
        self,
        host: str,
    ) -> bool:
        """Check whether a literal IP is disallowed."""
        try:
            address = ipaddress.ip_address(host)
        except ValueError:
            return False

        if (
            self.block_private_addresses
            and address.is_private
        ):
            return True

        if (
            self.block_loopback
            and address.is_loopback
        ):
            return True

        if (
            self.block_link_local
            and address.is_link_local
        ):
            return True

        return False

    @staticmethod
    def _domain_matches(
        host: str,
        domains: List[str],
    ) -> bool:
        """Match a hostname against a domain list."""
        for domain in domains:
            domain = domain.lower().strip().rstrip(".")

            if (
                host == domain
                or host.endswith("." + domain)
            ):
                return True

        return False
