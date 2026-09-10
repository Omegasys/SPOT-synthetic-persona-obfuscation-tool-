"""SPOT bounded synthetic DNS noise."""

from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Iterable, List


@dataclass
class DNSNoisePolicy:
    """Limits for synthetic DNS activity variation."""

    enabled: bool = False

    max_extra_queries: int = 10

    # Noise is restricted to domains explicitly supplied
    # by the caller. SPOT does not invent arbitrary destinations.
    allow_supplied_domains_only: bool = True


class DNSNoise:
    """Generate bounded variations of an existing DNS activity set."""

    def __init__(
        self,
        policy: DNSNoisePolicy | None = None,
        seed: int | None = None,
    ) -> None:
        self.policy = policy or DNSNoisePolicy()
        self.random = random.Random(seed)

    def generate(
        self,
        domains: Iterable[str],
        count: int | None = None,
    ) -> List[str]:
        """Select a bounded set of synthetic DNS destinations."""
        if not self.policy.enabled:
            return []

        available = [
            str(domain).strip().lower().rstrip(".")
            for domain in domains
            if str(domain).strip()
        ]

        if not available:
            return []

        maximum = min(
            self.policy.max_extra_queries,
            len(available),
        )

        requested = (
            maximum
            if count is None
            else max(0, min(count, maximum))
        )

        if requested == 0:
            return []

        return self.random.sample(
            available,
            requested,
        )

    def shuffle(
        self,
        domains: Iterable[str],
    ) -> List[str]:
        """Return a randomized copy of supplied domains."""
        values = list(domains)

        if not self.policy.enabled:
            return values

        self.random.shuffle(values)
        return values
