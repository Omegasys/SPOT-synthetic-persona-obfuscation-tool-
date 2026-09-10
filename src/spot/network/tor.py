"""SPOT Tor routing configuration."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TorConfig:
    """Configuration for a Tor-routed SPOT environment."""

    enabled: bool = True

    socks_host: str = "127.0.0.1"
    socks_port: int = 9050

    control_enabled: bool = False
    control_host: str = "127.0.0.1"
    control_port: int = 9051

    strict_mode: bool = True
    prevent_direct_connections: bool = True

    timeout_seconds: int = 60

    def validate(self) -> None:
        """Validate Tor configuration."""
        self._validate_port(
            self.socks_port,
            "socks_port",
        )

        if self.control_enabled:
            self._validate_port(
                self.control_port,
                "control_port",
            )

        if self.timeout_seconds < 1:
            raise ValueError(
                "Tor timeout must be at least 1 second."
            )

        if self.strict_mode:
            self.prevent_direct_connections = True

    def socks_endpoint(self) -> str:
        """Return the Tor SOCKS endpoint."""
        self.validate()

        return (
            f"socks5h://"
            f"{self.socks_host}:"
            f"{self.socks_port}"
        )

    def control_endpoint(self) -> str | None:
        """Return the optional Tor control endpoint."""
        self.validate()

        if not self.control_enabled:
            return None

        return (
            f"{self.control_host}:"
            f"{self.control_port}"
        )

    @staticmethod
    def _validate_port(
        port: int,
        name: str,
    ) -> None:
        """Validate a TCP port."""
        if not 1 <= port <= 65535:
            raise ValueError(
                f"{name} must be between 1 and 65535."
            )
