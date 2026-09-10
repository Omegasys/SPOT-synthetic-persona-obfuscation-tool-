"""SPOT proxy configuration."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass
class ProxyConfig:
    """Configuration for a synthetic activity proxy."""

    url: str
    enabled: bool = True

    username: str | None = None
    password: str | None = None

    timeout_seconds: int = 30

    def validate(self) -> None:
        """Validate proxy configuration."""
        parsed = urlparse(self.url)

        if parsed.scheme not in (
            "http",
            "https",
            "socks5",
            "socks5h",
        ):
            raise ValueError(
                "Unsupported proxy protocol."
            )

        if not parsed.hostname:
            raise ValueError(
                "Proxy URL must contain a hostname."
            )

        if not parsed.port:
            raise ValueError(
                "Proxy URL must contain an explicit port."
            )

        if not 1 <= parsed.port <= 65535:
            raise ValueError(
                "Proxy port is outside the valid range."
            )

        if self.timeout_seconds < 1:
            raise ValueError(
                "Proxy timeout must be at least 1 second."
            )

    def endpoint(self) -> str:
        """Return the configured proxy endpoint."""
        self.validate()
        parsed = urlparse(self.url)

        return f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"
