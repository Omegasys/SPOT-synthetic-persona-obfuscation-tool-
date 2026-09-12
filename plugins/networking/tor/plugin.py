from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import socket
from typing import Any, Mapping, Optional

from spot.plugins.interface import PluginMetadata, SPOTPlugin


class TorStatus(str, Enum):
    """Possible Tor plugin states."""

    DISABLED = "disabled"
    CONFIGURED = "configured"
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    BLOCKED = "blocked"
    ERROR = "error"


@dataclass
class TorConfig:
    """Configuration for a Tor SOCKS endpoint."""

    host: str = "127.0.0.1"
    port: int = 9050

    socks_version: int = 5

    enabled: bool = True
    strict: bool = True
    fail_closed: bool = True
    allow_direct_fallback: bool = False

    connect_timeout: float = 5.0

    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.host or not self.host.strip():
            raise ValueError("Tor host cannot be empty.")

        if not 1 <= self.port <= 65535:
            raise ValueError("Tor port must be between 1 and 65535.")

        if self.socks_version != 5:
            raise ValueError("Only SOCKS5 is supported.")

        if self.connect_timeout <= 0:
            raise ValueError("connect_timeout must be greater than zero.")

        if self.fail_closed and self.allow_direct_fallback:
            raise ValueError(
                "Direct fallback cannot be enabled with fail_closed."
            )


@dataclass
class TorRoute:
    """A validated Tor routing description."""

    host: str
    port: int
    socks_version: int
    strict: bool
    fail_closed: bool

    def as_proxy_url(self) -> str:
        """Return a SOCKS5 proxy URL."""

        return f"socks5://{self.host}:{self.port}"


@dataclass
class TorHealth:
    """Result of a Tor endpoint health check."""

    status: TorStatus
    host: str
    port: int
    message: str
    latency_ms: Optional[float] = None


class TorPlugin(SPOTPlugin):
    """
    SPOT Tor networking plugin.

    This plugin manages configuration and health checks for a Tor SOCKS
    endpoint. It does not modify host networking or silently fall back
    to direct networking.
    """

    metadata = PluginMetadata(
        id="network-tor",
        name="Tor Networking Plugin",
        version="0.1.0",
        description=(
            "Provides controlled Tor SOCKS routing integration for SPOT."
        ),
    )

    def __init__(
        self,
        config: Optional[TorConfig] = None,
    ) -> None:
        self.config = config or TorConfig()

        self._initialized = False
        self._running = False
        self._status = TorStatus.DISABLED

    def initialize(self, context: Any) -> bool:
        """Initialize the plugin with an SPOT plugin context."""

        try:
            self.config.validate()
        except ValueError:
            self._status = TorStatus.ERROR
            return False

        self.context = context
        self._initialized = True

        if self.config.enabled:
            self._status = TorStatus.CONFIGURED
        else:
            self._status = TorStatus.DISABLED

        return True

    def start(self) -> bool:
        """Start the plugin."""

        if not self._initialized:
            return False

        if not self.config.enabled:
            self._status = TorStatus.DISABLED
            return False

        self._running = True
        self._status = TorStatus.CONFIGURED

        return True

    def stop(self) -> bool:
        """Stop the plugin."""

        self._running = False

        if self.config.enabled:
            self._status = TorStatus.CONFIGURED
        else:
            self._status = TorStatus.DISABLED

        return True

    def health_check(self) -> bool:
        """Return whether the plugin itself is running."""

        return (
            self._initialized
            and self._running
            and self.config.enabled
        )

    @property
    def status(self) -> TorStatus:
        """Return the current plugin status."""

        return self._status

    def route(self) -> TorRoute:
        """
        Return a validated Tor route.

        This method only describes the route. It does not modify system
        routing.
        """

        if not self._initialized:
            raise RuntimeError("Tor plugin is not initialized.")

        if not self.config.enabled:
            raise RuntimeError("Tor networking is disabled.")

        self.config.validate()

        return TorRoute(
            host=self.config.host,
            port=self.config.port,
            socks_version=self.config.socks_version,
            strict=self.config.strict,
            fail_closed=self.config.fail_closed,
        )

    def proxy_url(self) -> str:
        """Return the configured SOCKS5 proxy URL."""

        return self.route().as_proxy_url()

    def check_endpoint(
        self,
        timeout: Optional[float] = None,
    ) -> TorHealth:
        """
        Check whether the configured Tor SOCKS endpoint accepts TCP
        connections.

        This does not perform an Internet request or modify routing.
        """

        if not self._initialized:
            return TorHealth(
                status=TorStatus.ERROR,
                host=self.config.host,
                port=self.config.port,
                message="Tor plugin is not initialized.",
            )

        if not self.config.enabled:
            return TorHealth(
                status=TorStatus.DISABLED,
                host=self.config.host,
                port=self.config.port,
                message="Tor networking is disabled.",
            )

        if not self._running:
            return TorHealth(
                status=TorStatus.UNAVAILABLE,
                host=self.config.host,
                port=self.config.port,
                message="Tor plugin is not running.",
            )

        try:
            self.config.validate()
        except ValueError as exc:
            self._status = TorStatus.ERROR

            return TorHealth(
                status=TorStatus.ERROR,
                host=self.config.host,
                port=self.config.port,
                message=str(exc),
            )

        connect_timeout = (
            self.config.connect_timeout
            if timeout is None
            else timeout
        )

        if connect_timeout <= 0:
            raise ValueError("timeout must be greater than zero.")

        import time

        start = time.monotonic()

        try:
            with socket.create_connection(
                (self.config.host, self.config.port),
                timeout=connect_timeout,
            ):
                pass

        except OSError as exc:
            self._status = TorStatus.UNAVAILABLE

            return TorHealth(
                status=TorStatus.UNAVAILABLE,
                host=self.config.host,
                port=self.config.port,
                message=str(exc),
            )

        latency_ms = (time.monotonic() - start) * 1000

        self._status = TorStatus.AVAILABLE

        return TorHealth(
            status=TorStatus.AVAILABLE,
            host=self.config.host,
            port=self.config.port,
            message="Tor SOCKS endpoint is reachable.",
            latency_ms=latency_ms,
        )

    def can_fallback_direct(self) -> bool:
        """
        Return whether direct networking is allowed.

        The default and recommended result is False.
        """

        return (
            not self.config.fail_closed
            and self.config.allow_direct_fallback
        )

    def routing_summary(self) -> dict[str, Any]:
        """Return a non-sensitive routing summary."""

        return {
            "enabled": self.config.enabled,
            "running": self._running,
            "status": self._status.value,
            "host": self.config.host,
            "port": self.config.port,
            "socks_version": self.config.socks_version,
            "strict": self.config.strict,
            "fail_closed": self.config.fail_closed,
            "allow_direct_fallback": self.config.allow_direct_fallback,
            "direct_fallback_allowed": self.can_fallback_direct(),
        }


PLUGIN = TorPlugin()
