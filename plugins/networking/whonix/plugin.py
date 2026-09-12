from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import socket
import time
from typing import Any, Optional

from spot.plugins.interface import PluginMetadata, SPOTPlugin


class WhonixStatus(str, Enum):
    """Possible Whonix plugin states."""

    DISABLED = "disabled"
    CONFIGURED = "configured"
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    BLOCKED = "blocked"
    ERROR = "error"


class WhonixTopology(str, Enum):
    """Supported Whonix deployment topologies."""

    GENERIC = "generic"
    QUBES = "qubes"


@dataclass
class WhonixConfig:
    """Configuration for a Whonix networking integration."""

    topology: WhonixTopology = WhonixTopology.QUBES

    gateway_host: str = "sys-whonix"
    gateway_port: int = 9050

    workstation_name: str = "anon-whonix"

    enabled: bool = True

    require_gateway: bool = True
    require_tor: bool = True

    strict: bool = True
    fail_closed: bool = True

    allow_direct_fallback: bool = False

    prevent_dns_bypass: bool = True

    connect_timeout: float = 5.0

    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.gateway_host or not self.gateway_host.strip():
            raise ValueError("Whonix gateway host cannot be empty.")

        if not 1 <= self.gateway_port <= 65535:
            raise ValueError(
                "Whonix gateway port must be between 1 and 65535."
            )

        if not self.workstation_name or not self.workstation_name.strip():
            raise ValueError("Whonix workstation name cannot be empty.")

        if self.connect_timeout <= 0:
            raise ValueError("connect_timeout must be greater than zero.")

        if self.fail_closed and self.allow_direct_fallback:
            raise ValueError(
                "Direct fallback cannot be enabled with fail_closed."
            )

        if self.topology == WhonixTopology.QUBES:
            if not self.gateway_host.strip():
                raise ValueError(
                    "Qubes Whonix topology requires a Gateway."
                )


@dataclass
class WhonixRoute:
    """A validated Whonix routing description."""

    topology: WhonixTopology
    gateway_host: str
    gateway_port: int
    workstation_name: str
    require_gateway: bool
    require_tor: bool
    strict: bool
    fail_closed: bool
    prevent_dns_bypass: bool

    def as_endpoint(self) -> str:
        """Return the configured Gateway endpoint."""

        return f"{self.gateway_host}:{self.gateway_port}"


@dataclass
class WhonixHealth:
    """Result of a Whonix integration health check."""

    status: WhonixStatus
    gateway_host: str
    gateway_port: int
    workstation_name: str
    message: str
    latency_ms: Optional[float] = None


class WhonixPlugin(SPOTPlugin):
    """
    SPOT Whonix networking integration plugin.

    This plugin validates and describes a Whonix network path. It does
    not directly modify host networking, Qubes policy, firewall rules,
    routing tables, or privileged system state.
    """

    metadata = PluginMetadata(
        id="network-whonix",
        name="Whonix Networking Plugin",
        version="0.1.0",
        description=(
            "Provides controlled Whonix networking integration for SPOT."
        ),
    )

    def __init__(
        self,
        config: Optional[WhonixConfig] = None,
    ) -> None:
        self.config = config or WhonixConfig()

        self._initialized = False
        self._running = False
        self._status = WhonixStatus.DISABLED

    def initialize(self, context: Any) -> bool:
        """Initialize the plugin with an SPOT plugin context."""

        try:
            self.config.validate()
        except ValueError:
            self._status = WhonixStatus.ERROR
            return False

        self.context = context
        self._initialized = True

        if self.config.enabled:
            self._status = WhonixStatus.CONFIGURED
        else:
            self._status = WhonixStatus.DISABLED

        return True

    def start(self) -> bool:
        """Start the Whonix integration."""

        if not self._initialized:
            return False

        if not self.config.enabled:
            self._status = WhonixStatus.DISABLED
            return False

        self._running = True
        self._status = WhonixStatus.CONFIGURED

        return True

    def stop(self) -> bool:
        """Stop the Whonix integration."""

        self._running = False

        if self.config.enabled:
            self._status = WhonixStatus.CONFIGURED
        else:
            self._status = WhonixStatus.DISABLED

        return True

    def health_check(self) -> bool:
        """Return whether the plugin is initialized and running."""

        return (
            self._initialized
            and self._running
            and self.config.enabled
        )

    @property
    def status(self) -> WhonixStatus:
        """Return the current plugin status."""

        return self._status

    def route(self) -> WhonixRoute:
        """
        Return a validated Whonix routing description.

        This does not modify system networking.
        """

        if not self._initialized:
            raise RuntimeError(
                "Whonix plugin is not initialized."
            )

        if not self.config.enabled:
            raise RuntimeError(
                "Whonix networking is disabled."
            )

        self.config.validate()

        return WhonixRoute(
            topology=self.config.topology,
            gateway_host=self.config.gateway_host,
            gateway_port=self.config.gateway_port,
            workstation_name=self.config.workstation_name,
            require_gateway=self.config.require_gateway,
            require_tor=self.config.require_tor,
            strict=self.config.strict,
            fail_closed=self.config.fail_closed,
            prevent_dns_bypass=self.config.prevent_dns_bypass,
        )

    def gateway_endpoint(self) -> str:
        """Return the configured Whonix Gateway endpoint."""

        return self.route().as_endpoint()

    def check_gateway(
        self,
        timeout: Optional[float] = None,
    ) -> WhonixHealth:
        """
        Check whether the configured Gateway endpoint accepts a TCP
        connection.

        This does not make an Internet request.
        """

        if not self._initialized:
            return WhonixHealth(
                status=WhonixStatus.ERROR,
                gateway_host=self.config.gateway_host,
                gateway_port=self.config.gateway_port,
                workstation_name=self.config.workstation_name,
                message="Whonix plugin is not initialized.",
            )

        if not self.config.enabled:
            return WhonixHealth(
                status=WhonixStatus.DISABLED,
                gateway_host=self.config.gateway_host,
                gateway_port=self.config.gateway_port,
                workstation_name=self.config.workstation_name,
                message="Whonix networking is disabled.",
            )

        if not self._running:
            return WhonixHealth(
                status=WhonixStatus.UNAVAILABLE,
                gateway_host=self.config.gateway_host,
                gateway_port=self.config.gateway_port,
                workstation_name=self.config.workstation_name,
                message="Whonix plugin is not running.",
            )

        try:
            self.config.validate()
        except ValueError as exc:
            self._status = WhonixStatus.ERROR

            return WhonixHealth(
                status=WhonixStatus.ERROR,
                gateway_host=self.config.gateway_host,
                gateway_port=self.config.gateway_port,
                workstation_name=self.config.workstation_name,
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
                (
                    self.config.gateway_host,
                    self.config.gateway_port,
                ),
                timeout=connect_timeout,
            ):
                pass

        except OSError as exc:
            self._status = WhonixStatus.UNAVAILABLE

            return WhonixHealth(
                status=WhonixStatus.UNAVAILABLE,
                gateway_host=self.config.gateway_host,
                gateway_port=self.config.gateway_port,
                workstation_name=self.config.workstation_name,
                message=str(exc),
            )

        latency_ms = (time.monotonic() - started) * 1000

        self._status = WhonixStatus.AVAILABLE

        return WhonixHealth(
            status=WhonixStatus.AVAILABLE,
            gateway_host=self.config.gateway_host,
            gateway_port=self.config.gateway_port,
            workstation_name=self.config.workstation_name,
            message="Whonix Gateway endpoint is reachable.",
            latency_ms=latency_ms,
        )

    def can_fallback_direct(self) -> bool:
        """
        Return whether direct networking is permitted.

        The default and recommended result is False.
        """

        return (
            not self.config.fail_closed
            and self.config.allow_direct_fallback
        )

    def network_allowed(self) -> bool:
        """
        Return whether the Whonix route is currently permitted by
        plugin-level state.

        This does not perform a health check.
        """

        if not self._initialized:
            return False

        if not self._running:
            return False

        if not self.config.enabled:
            return False

        return True

    def topology_summary(self) -> dict[str, Any]:
        """Return a non-sensitive topology summary."""

        return {
            "topology": self.config.topology.value,
            "gateway_host": self.config.gateway_host,
            "gateway_port": self.config.gateway_port,
            "workstation_name": self.config.workstation_name,
            "enabled": self.config.enabled,
            "running": self._running,
            "status": self._status.value,
            "require_gateway": self.config.require_gateway,
            "require_tor": self.config.require_tor,
            "strict": self.config.strict,
            "fail_closed": self.config.fail_closed,
            "allow_direct_fallback": (
                self.config.allow_direct_fallback
            ),
            "direct_fallback_allowed": (
                self.can_fallback_direct()
            ),
            "prevent_dns_bypass": (
                self.config.prevent_dns_bypass
            ),
        }

    def is_fail_closed(self) -> bool:
        """Return whether the integration uses fail-closed behavior."""

        return self.config.fail_closed

    def emergency_stop(self) -> bool:
        """
        Place the plugin into a blocked state.

        Actual network shutdown is performed by the platform integration
        layer.
        """

        self._running = False
        self._status = WhonixStatus.BLOCKED

        return True


PLUGIN = WhonixPlugin()
