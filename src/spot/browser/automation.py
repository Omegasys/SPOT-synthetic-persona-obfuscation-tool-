"""SPOT bounded browser automation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List
from urllib.parse import urlparse


@dataclass
class AutomationPolicy:
    """Safety limits for browser automation."""

    enabled: bool = True

    max_pages: int = 10
    max_actions: int = 25

    allow_navigation: bool = True
    allow_forms: bool = False
    allow_file_uploads: bool = False
    allow_downloads: bool = False

    allowed_domains: List[str] = field(
        default_factory=list
    )


@dataclass
class Automation:
    """Create bounded browser automation plans.

    This class does not execute browser actions itself.
    An actual browser adapter must enforce the returned plan
    through the configured browser and network security layers.
    """

    policy: AutomationPolicy = field(
        default_factory=AutomationPolicy
    )

    def navigation(
        self,
        url: str,
    ) -> Dict[str, Any]:
        """Create a navigation request."""
        if not self.policy.enabled:
            raise RuntimeError(
                "Browser automation is disabled."
            )

        if not self.policy.allow_navigation:
            raise PermissionError(
                "Navigation is disabled by policy."
            )

        parsed = urlparse(url)

        if parsed.scheme not in (
            "http",
            "https",
        ):
            raise ValueError(
                "Only HTTP(S) navigation is supported."
            )

        if not parsed.netloc:
            raise ValueError(
                "Navigation URL must include a host."
            )

        if not self._domain_allowed(
            parsed.hostname or ""
        ):
            raise PermissionError(
                "Destination is not allowed by browser policy."
            )

        return {
            "action": "navigate",
            "url": url,
            "synthetic": True,
        }

    def click(
        self,
        selector: str,
    ) -> Dict[str, Any]:
        """Create a bounded click request."""
        self._check_action()

        if not selector:
            raise ValueError(
                "Selector cannot be empty."
            )

        return {
            "action": "click",
            "selector": selector,
            "synthetic": True,
        }

    def type_text(
        self,
        selector: str,
        text: str,
    ) -> Dict[str, Any]:
        """Create a bounded text-entry request."""
        self._check_action()

        if not selector:
            raise ValueError(
                "Selector cannot be empty."
            )

        if not self.policy.allow_forms:
            raise PermissionError(
                "Form interaction is disabled by policy."
            )

        return {
            "action": "type",
            "selector": selector,
            "text": text,
            "synthetic": True,
        }

    def _check_action(self) -> None:
        if not self.policy.enabled:
            raise RuntimeError(
                "Browser automation is disabled."
            )

    def _domain_allowed(
        self,
        domain: str,
    ) -> bool:
        """Check the optional domain allowlist."""
        if not self.policy.allowed_domains:
            return True

        domain = domain.lower()

        return any(
            domain == allowed.lower()
            or domain.endswith(
                "." + allowed.lower()
            )
            for allowed in self.policy.allowed_domains
        )
