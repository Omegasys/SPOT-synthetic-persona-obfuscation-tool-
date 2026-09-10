"""SPOT DNS policy and request handling."""

from __future__ import annotations

from dataclasses import dataclass, field
import ipaddress
from typing import List


@dataclass
class DNSPolicy:
    """Policy controlling synthetic DNS requests."""

    enabled: bool = True
    max_queries: int = 100

    block_private: bool = True
    block_loopback: bool = True
    block_link_local: bool = True

    allowed_domains: List[str] = field(
        default_factory=list
    )
    blocked_domains: List[str] = field(
        default_factory=list
    )


@dataclass
class DNSRequest:
    """A policy-checked DNS request."""

    domain: str
    record_type: str = "A"


class DNSManager:
    """Prepare DNS requests without performing resolution."""

    def __init__(
        self,
        policy: DNSPolicy | None = None,
    ) -> None:
        self.policy = policy or DNSPolicy()
        self.query_count = 0

    def validate_domain(
        self,
        domain: str,
    ) -> bool:
        """Check whether a domain is allowed."""
        if not self.policy.enabled:
            return False

        domain = self._normalize(domain)

        if not domain:
            return False

        if self._looks_like_ip(domain):
            return not self._blocked_ip(domain)

        if self._matches(
            domain,
            self.policy.blocked_domains,
        ):
            return False

        if self.policy.allowed_domains:
            return self._matches(
                domain,
                self.policy.allowed_domains,
            )

        return True

    def prepare(
        self,
        domain: str,
        record_type: str = "A",
    ) -> DNSRequest:
        """Prepare a policy-checked DNS request."""
        if self.query_count >= self.policy.max_queries:
            raise RuntimeError(
                "DNS query limit has been reached."
            )

        if not self.validate_domain(domain):
            raise PermissionError(
                "DNS destination is blocked by policy."
            )

        record_type = record_type.upper()

        allowed_types = {
            "A",
            "AAAA",
            "CNAME",
            "MX",
            "TXT",
        }

        if record_type not in allowed_types:
            raise ValueError(
                f"Unsupported DNS record type: {record_type}"
            )

        self.query_count += 1

        return DNSRequest(
            domain=self._normalize(domain),
            record_type=record_type,
        )

    def reset(self) -> None:
        """Reset the query counter."""
        self.query_count = 0

    @staticmethod
    def _normalize(domain: str) -> str:
        return domain.strip().lower().rstrip(".")

    @staticmethod
    def _looks_like_ip(domain: str) -> bool:
        try:
            ipaddress.ip_address(domain)
            return True
        except ValueError:
            return False

    def _blocked_ip(self, address: str) -> bool:
        try:
            ip = ipaddress.ip_address(address)
        except ValueError:
            return True

        if self.policy.block_private and ip.is_private:
            return True

        if self.policy.block_loopback and ip.is_loopback:
            return True

        if self.policy.block_link_local and ip.is_link_local:
            return True

        return False

    @staticmethod
    def _matches(
        domain: str,
        rules: List[str],
    ) -> bool:
        for rule in rules:
            rule = rule.strip().lower().rstrip(".")

            if (
                domain == rule
                or domain.endswith("." + rule)
            ):
                return True

        return False
