from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import socket
import time
from typing import Any, Optional
from urllib.parse import quote


class ProxyType(str, Enum):
    """Supported proxy protocols."""

    HTTP = "http"
    HTTPS = "https"
    SOCKS5 = "socks5"
    SOCKS5H = "socks5h"


class ProxyStatus(str, Enum):
    """Possible proxy plugin states."""

    DISABLED = "disabled"
    CONFIGURED = "configured"
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    BLOCKED = "blocked"
    ERROR = "error"


@dataclass
class ProxyConfig:
    """Configuration for a controlled proxy endpoint."""

    proxy_type: ProxyType = ProxyType.SOCKS5

    host: str = "127.0.0.1"
    port: int = 8080

    enabled: bool = True

    strict: bool = True
    fail_closed: bool = True
    allow_direct_fallback: bool = False

    # Authentication is deliberately disabled by default.
    authentication_enabled: bool = False
    username: Optional[str] = None
    password: Optional[str] = None

    connect_timeout: float = 5.0

    # Keep proxy chaining disabled unless explicitly supported by a
    # future controlled backend.
    allow_proxy_chaining: bool = False

    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.host or not self.host.strip():
            raise ValueError("Proxy host cannot be empty.")

        if not 1 <= self.port <= 65535:
            raise ValueError(
                "Proxy port must be between 1 and 65535."
            )

        if self.connect_timeout <= 0:
            raise ValueError(
                "connect_timeout must be greater than zero."
            )

        if self.fail_closed and self.allow_direct_fallback:
            raise ValueError(
                "Direct fallback cannot be enabled with fail_closed."
            )

        if not isinstance(self.proxy_type, ProxyType):
            try:
                ProxyType(self.proxy_type)
            except ValueError as exc:
                raise ValueError(
                    "Unsupported proxy type."
                ) from exc

        if self.authentication_enabled:
            if not self.username:
                raise ValueError(
                    "Proxy username is required when authentication "
                    "is enabled."
                )

            if self.password is None:
                raise ValueError(
                    "Proxy password is required when authentication "
                    "is enabled."
                )
        else:
            if self.username is not None:
                raise ValueError(
                    "Username cannot be configured while proxy "
                    "authentication is disabled."
                )

            if self.password is not None:
                raise ValueError(
                    "Password cannot be configured while proxy "
                    "authentication is disabled."
                )

        if self.allow_proxy_chaining:
            raise ValueError(
                "Proxy chaining is not supported by this plugin."
            )


@dataclass
class ProxyRoute:
    """A validated proxy routing description."""

    proxy_type: ProxyType
    host: str
    port: int

    strict: bool
    fail_closed: bool

    authentication_enabled: bool = False
    username: Optional[str] = None

    def as_url(
        self,
        include_credentials: bool = False,
    ) -> str:
        """
        Return a proxy URL.

        Credentials are excluded by default.
        """

        scheme = self.proxy_type.value

        authority = self.host

        if self.authentication_enabled and include_credentials:
            if self.username is None:
                raise ValueError(
                    "Proxy username is unavailable."
                )

            authority = (
                f"{quote(self.username, safe='')}"
                f"@{authority}"
            )

        return f"{scheme}://{authority}:{self.port}"


@dataclass
class ProxyHealth:
    """Result of a proxy endpoint health check."""

    status: ProxyStatus
    proxy_type: ProxyType
    host: str
    port: int
    message: str
    latency_ms: Optional[float] = None


class ProxyPlugin:
    """
    SPOT generic proxy networking plugin.

    This plugin validates and describes proxy routes and can perform
    bounded endpoint health checks.

    It does not modify host networking, firewall rules, routing
    tables, or DNS configuration.
    """

    metadata = type(
        "PluginMetadata",
        (),
        {
            "id": "network-proxy",
            "name": "Proxy Networking Plugin",
            "version": "0.1.0",
            "description": (
                "Provides controlled HTTP, HTTPS, SOCKS5, and "
                "SOCKS5H proxy integration for SPOT."
            ),
        },
    )

    def __init__(
        self,
        config: Optional[ProxyConfig] = None,
    ) -> None:
        self.config = config or ProxyConfig()

        self._initialized = False
        self._running = False
        self._status = ProxyStatus.DISABLED

        self.context: Any = None

    def initialize(self, context: Any) -> bool:
        """Initialize the plugin."""

        try:
            self.config.validate()
        except ValueError:
            self._status = ProxyStatus.ERROR
            return False

        self.context = context
        self._initialized = True

        if self.config.enabled:
            self._status = ProxyStatus.CONFIGURED
        else:
            self._status = ProxyStatus.DISABLED

        return True

    def start(self) -> bool:
        """Start the proxy integration."""

        if not self._initialized:
            return False

        if not self.config.enabled:
            self._status = ProxyStatus.DISABLED
            return False

        try:
            self.config.validate()
        except ValueError:
            self._status = ProxyStatus.ERROR
            return False

        self._running = True
        self._status = ProxyStatus.CONFIGURED

        return True

    def stop(self) -> bool:
        """Stop the proxy integration."""

        self._running = False

        if self.config.enabled:
            self._status = ProxyStatus.CONFIGURED
        else:
            self._status = ProxyStatus.DISABLED

        return True

    def health_check(self) -> bool:
        """Return whether the plugin is initialized and running."""

        return (
            self._initialized
            and self._running
            and self.config.enabled
        )

    @property
    def status(self) -> ProxyStatus:
        """Return the current proxy status."""

        return self._status

    def route(self) -> ProxyRoute:
        """
        Return a validated proxy route.

        This method only describes the route.
        It does not modify system networking.
        """

        if not self._initialized:
            raise RuntimeError(
                "Proxy plugin is not initialized."
            )

        if not self.config.enabled:
            raise RuntimeError(
                "Proxy networking is disabled."
            )

        self.config.validate()

        return ProxyRoute(
            proxy_type=self.config.proxy_type,
            host=self.config.host,
            port=self.config.port,
            strict=self.config.strict,
            fail_closed=self.config.fail_closed,
            authentication_enabled=(
                self.config.authentication_enabled
            ),
            username=self.config.username,
        )

    def proxy_url(self) -> str:
        """Return the proxy URL without credentials."""

        return self.route().as_url(
            include_credentials=False
        )

    def check_endpoint(
        self,
        timeout: Optional[float] = None,
    ) -> ProxyHealth:
        """
        Check whether the configured proxy endpoint accepts a TCP
        connection.

        This does not send proxy traffic or perform an Internet request.
        """

        if not self._initialized:
            return ProxyHealth(
                status=ProxyStatus.ERROR,
                proxy_type=self.config.proxy_type,
                host=self.config.host,
                port=self.config.port,
                message="Proxy plugin is not initialized.",
            )

        if not self.config.enabled:
            return ProxyHealth(
                status=ProxyStatus.DISABLED,
                proxy_type=self.config.proxy_type,
                host=self.config.host,
                port=self.config.port,
                message="Proxy networking is disabled.",
            )

        if not self._running:
            return ProxyHealth(
                status=ProxyStatus.UNAVAILABLE,
                proxy_type=self.config.proxy_type,
                host=self.config.host,
                port=self.config.port,
                message="Proxy plugin is not running.",
            )

        try:
            self.config.validate()
        except ValueError as exc:
            self._status = ProxyStatus.ERROR

            return ProxyHealth(
                status=ProxyStatus.ERROR,
                proxy_type=self.config.proxy_type,
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
            raise ValueError(
                "timeout must be greater than zero."
            )

        started = time.monotonic()

        try:
            with socket.create_connection(
                (self.config.host, self.config.port),
                timeout=connect_timeout,
            ):
                pass

        except OSError as exc:
            self._status = ProxyStatus.UNAVAILABLE

            return ProxyHealth(
                status=ProxyStatus.UNAVAILABLE,
                proxy_type=self.config.proxy_type,
                host=self.config.host,
                port=self.config.port,
                message=str(exc),
            )

        latency_ms = (
            time.monotonic() - started
        ) * 1000

        self._status = ProxyStatus.AVAILABLE

        return ProxyHealth(
            status=ProxyStatus.AVAILABLE,
            proxy_type=self.config.proxy_type,
            host=self.config.host,
            port=self.config.port,
            message="Proxy endpoint is reachable.",
            latency_ms=latency_ms,
        )

    def can_fallback_direct(self) -> bool:
        """
        Return whether direct networking is explicitly permitted.

        The recommended result is False.
        """

        return (
            not self.config.fail_closed
            and self.config.allow_direct_fallback
        )

    def network_allowed(self) -> bool:
        """Return whether plugin-level network use is permitted."""

        return (
            self._initialized
            and self._running
            and self.config.enabled
        )

    def emergency_stop(self) -> bool:
        """
        Block the plugin.

        Actual network shutdown is delegated to the platform backend.
        """

        self._running = False
        self._status = ProxyStatus.BLOCKED

        return True

    def routing_summary(self) -> dict[str, Any]:
        """
        Return a non-sensitive routing summary.

        Authentication secrets are never included.
        """

        return {
            "proxy_type": self.config.proxy_type.value,
            "host": self.config.host,
            "port": self.config.port,
            "enabled": self.config.enabled,
            "running": self._running,
            "status": self._status.value,
            "strict": self.config.strict,
            "fail_closed": self.config.fail_closed,
            "allow_direct_fallback": (
                self.config.allow_direct_fallback
            ),
            "direct_fallback_allowed": (
                self.can_fallback_direct()
            ),
            "authentication_enabled": (
                self.config.authentication_enabled
            ),
            "allow_proxy_chaining": (
                self.config.allow_proxy_chaining
            ),
        }


PLUGIN = ProxyPlugin()
