"""SPOT synthetic DNS activity."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List


@dataclass
class DNSActivity:
    """Prepare bounded synthetic DNS activity.

    Actual DNS resolution is delegated to the network layer so that
    SPOT cannot accidentally bypass the configured network boundary.
    """

    name: str = "dns"

    def prepare(
        self,
        domains: Iterable[str],
        max_queries: int = 10,
        **_: Any,
    ) -> Dict[str, Any]:
        """Prepare synthetic DNS queries."""
        if max_queries < 1:
            raise ValueError(
                "max_queries must be at least 1."
            )

        selected: List[str] = []

        for domain in domains:
            domain = str(domain).strip().lower()

            if not domain:
                continue

            # Keep this layer intentionally simple. The network
            # policy layer is responsible for final destination
            # validation and blocking private/local destinations.
            selected.append(domain)

            if len(selected) >= max_queries:
                break

        return {
            "type": self.name,
            "domains": selected,
            "max_queries": max_queries,
            "synthetic": True,
            "requires_execution": True,
            "network_policy_required": True,
        }
