"""SPOT declarative firewall policy."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class FirewallAction(str, Enum):
    """Possible firewall policy actions."""

    ALLOW = "allow"
    DENY = "deny"


@dataclass
class FirewallRule:
    """A declarative firewall rule."""

    name: str
    action: FirewallAction

    destination: str | None = None
    port: int | None = None
    protocol: str | None = None

    enabled: bool = True

    def matches(
        self,
        destination: str,
        port: int | None = None,
        protocol: str | None = None,
    ) -> bool:
        """Determine whether this rule matches a request."""
        if not self.enabled:
            return False

        if (
            self.destination is not None
            and self.destination != destination
        ):
            return False

        if (
            self.port is not None
            and self.port != port
        ):
            return False

        if (
            self.protocol is not None
            and self.protocol.lower()
            != (protocol or "").lower()
        ):
            return False

        return True


@dataclass
class FirewallPolicy:
    """Declarative network firewall policy."""

    enabled: bool = True

    default_action: FirewallAction = (
        FirewallAction.DENY
    )

    rules: List[FirewallRule] = field(
        default_factory=list
    )

    def add_rule(
        self,
        rule: FirewallRule,
    ) -> None:
        """Add a firewall rule."""
        self.rules.append(rule)

    def remove_rule(
        self,
        name: str,
    ) -> None:
        """Remove rules with a matching name."""
        self.rules = [
            rule
            for rule in self.rules
            if rule.name != name
        ]

    def evaluate(
        self,
        destination: str,
        port: int | None = None,
        protocol: str | None = None,
    ) -> FirewallAction:
        """Evaluate a connection against the policy."""
        if not self.enabled:
            return FirewallAction.DENY

        # First matching rule wins.
        for rule in self.rules:
            if rule.matches(
                destination,
                port,
                protocol,
            ):
                return rule.action

        return self.default_action

    def allows(
        self,
        destination: str,
        port: int | None = None,
        protocol: str | None = None,
    ) -> bool:
        """Return whether a connection is allowed."""
        return (
            self.evaluate(
                destination,
                port,
                protocol,
            )
            == FirewallAction.ALLOW
        )
