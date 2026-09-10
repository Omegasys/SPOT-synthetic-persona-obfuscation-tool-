"""SPOT network manager."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .proxy import ProxyConfig
from .routing import NetworkMode, RoutingPolicy
from .tor import TorConfig
from .whonix import WhonixConfig


@dataclass
class NetworkStatus:
    """Current network state."""

    available: bool = False
    healthy: bool = False
    mode: NetworkMode = NetworkMode.DISABLED
    message: str = ""


class NetworkManager:
    """Manage SPOT network routing policies."""

    def __init__(
        self,
        policy: RoutingPolicy | None = None,
    ) -> None:
        self.policy = policy or RoutingPolicy()
        self.status = NetworkStatus(
            mode=self.policy.mode
        )

        self.proxy: ProxyConfig | None = None
        self.tor: TorConfig | None = None
        self.whonix: WhonixConfig | None = None

    def configure_proxy(
        self,
        config: ProxyConfig,
    ) -> None:
        """Configure an optional proxy route."""
        config.validate()
        self.proxy = config

    def configure_tor(
        self,
        config: TorConfig,
    ) -> None:
        """Configure a Tor route."""
        config.validate()
        self.tor = config

    def configure_whonix(
        self,
        config: WhonixConfig,
    ) -> None:
        """Configure a Whonix route."""
        config.validate()
        self.whonix = config

    def start(self) -> None:
        """Enable the configured network policy."""
        self.policy.validate()

        if self.policy.mode == NetworkMode.DISABLED:
            self.status = NetworkStatus(
                available=False,
                healthy=False,
                mode=self.policy.mode,
                message="Network access is disabled.",
            )
            return

        self.status = NetworkStatus(
            available=True,
            healthy=False,
            mode=self.policy.mode,
            message="Network configured; health check required.",
        )

    def mark_healthy(
        self,
        message: str = "Network is healthy.",
    ) -> None:
        """Mark the configured route as healthy."""
        if not self.status.available:
            raise RuntimeError(
                "Cannot mark an unavailable network as healthy."
            )

        self.status.healthy = True
        self.status.message = message

    def mark_unhealthy(
        self,
        message: str = "Network health check failed.",
    ) -> None:
        """Mark the route as unhealthy."""
        self.status.healthy = False
        self.status.message = message

        if self.policy.fail_closed:
            self.status.available = False

    def stop(self) -> None:
        """Disable network access."""
        self.status = NetworkStatus(
            available=False,
            healthy=False,
            mode=NetworkMode.DISABLED,
            message="Network access stopped.",
        )

    def can_connect(self) -> bool:
        """Return whether connections may be attempted."""
        return (
            self.status.available
            and self.status.healthy
        )

    def allowed_destination(
        self,
        host: str,
    ) -> bool:
        """Check whether a destination is permitted."""
        return self.policy.destination_allowed(host)

    def active_mode(self) -> str:
        """Return the active routing mode."""
        return self.policy.mode.value

    def summary(self) -> Dict[str, object]:
        """Return a network status summary."""
        return {
            "available": self.status.available,
            "healthy": self.status.healthy,
            "mode": self.status.mode.value,
            "message": self.status.message,
            "fail_closed": self.policy.fail_closed,
        }
