"""SPOT synthetic browser cookies."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List


@dataclass
class Cookie:
    """A synthetic browser cookie."""

    name: str
    value: str
    domain: str

    path: str = "/"
    secure: bool = True
    http_only: bool = True

    created_at: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )


class CookieJar:
    """Isolated cookie storage for one synthetic profile."""

    def __init__(
        self,
        enabled: bool = True,
        max_cookies: int = 100,
    ) -> None:
        self.enabled = enabled
        self.max_cookies = max(
            1,
            max_cookies,
        )

        self._cookies: Dict[
            tuple[str, str, str],
            Cookie,
        ] = {}

    def set(
        self,
        cookie: Cookie,
    ) -> None:
        """Store a synthetic cookie."""
        if not self.enabled:
            return

        key = (
            cookie.domain,
            cookie.path,
            cookie.name,
        )

        self._cookies[key] = cookie
        self._enforce_limit()

    def get(
        self,
        domain: str,
        name: str,
        path: str = "/",
    ) -> Cookie | None:
        """Return a cookie for a domain."""
        if not self.enabled:
            return None

        return self._cookies.get(
            (
                domain,
                path,
                name,
            )
        )

    def delete(
        self,
        domain: str,
        name: str,
        path: str = "/",
    ) -> None:
        """Delete one cookie."""
        self._cookies.pop(
            (
                domain,
                path,
                name,
            ),
            None,
        )

    def clear(self) -> None:
        """Delete all cookies."""
        self._cookies.clear()

    def all(self) -> List[Cookie]:
        """Return all stored cookies."""
        return list(
            self._cookies.values()
        )

    def _enforce_limit(self) -> None:
        while len(self._cookies) > self.max_cookies:
            oldest_key = next(
                iter(self._cookies)
            )
            del self._cookies[oldest_key]
