from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional
from urllib.parse import urlparse

from spot.plugins.interface import PluginMetadata, SPOTPlugin


@dataclass
class BrowserRequest:
    """A bounded synthetic browser navigation request."""

    url: str
    persona_id: Optional[str] = None
    max_pages: int = 10
    allow_downloads: bool = False
    allow_uploads: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.url:
            raise ValueError("Browser URL cannot be empty.")

        parsed = urlparse(self.url)

        if parsed.scheme not in {"http", "https"}:
            raise ValueError("Only HTTP and HTTPS URLs are permitted.")

        if not parsed.netloc:
            raise ValueError("Browser URL must contain a host.")

        if self.max_pages < 1:
            raise ValueError("max_pages must be at least 1.")

        if self.max_pages > 100:
            raise ValueError("max_pages exceeds the plugin safety limit.")

        if self.allow_uploads:
            raise ValueError(
                "File uploads are disabled by the browser plugin."
            )


@dataclass
class BrowserSession:
    """Local representation of a synthetic browser session."""

    session_id: str
    persona_id: Optional[str] = None
    active: bool = False
    pages_visited: int = 0
    actions_performed: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class BrowserResult:
    """Provider-neutral result of a browser activity request."""

    success: bool
    request: BrowserRequest
    session: Optional[BrowserSession] = None
    error: Optional[str] = None


class BrowserPlugin(SPOTPlugin):
    """
    SPOT synthetic browser activity plugin.

    This plugin prepares bounded browser activity. Actual browser execution
    should be performed by an approved SPOT browser backend.
    """

    metadata = PluginMetadata(
        id="activity-browser",
        name="Browser Activity Plugin",
        version="0.1.0",
        description=(
            "Provides bounded, isolated synthetic browser activity."
        ),
    )

    def __init__(
        self,
        max_pages: int = 10,
        max_actions: int = 25,
    ) -> None:
        self.max_pages = max_pages
        self.max_actions = max_actions

        self._initialized = False
        self._running = False
        self._session_counter = 0
        self._sessions: dict[str, BrowserSession] = {}

    def initialize(self, context: Any) -> bool:
        """Initialize the plugin with an SPOT plugin context."""
        self.context = context
        self._initialized = True
        return True

    def start(self) -> bool:
        """Start the plugin."""
        if not self._initialized:
            return False

        self._running = True
        return True

    def stop(self) -> bool:
        """Stop the plugin and close plugin-managed sessions."""
        self._running = False

        for session in self._sessions.values():
            session.active = False

        return True

    def health_check(self) -> bool:
        """Return whether the plugin is operational."""
        return self._initialized and self._running

    def create_session(
        self,
        persona_id: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> BrowserSession:
        """Create a local synthetic browser session."""

        if not self._running:
            raise RuntimeError("Browser plugin is not running.")

        self._session_counter += 1
        session_id = f"browser-session-{self._session_counter:04d}"

        session = BrowserSession(
            session_id=session_id,
            persona_id=persona_id,
            active=True,
            metadata=dict(metadata or {}),
        )

        self._sessions[session_id] = session

        return session

    def get_session(self, session_id: str) -> Optional[BrowserSession]:
        """Return a managed browser session."""
        return self._sessions.get(session_id)

    def stop_session(self, session_id: str) -> bool:
        """Stop a managed browser session."""
        session = self._sessions.get(session_id)

        if session is None:
            return False

        session.active = False
        return True

    def prepare_navigation(
        self,
        url: str,
        persona_id: Optional[str] = None,
        max_pages: Optional[int] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> BrowserRequest:
        """Prepare a bounded browser navigation request."""

        if not isinstance(url, str):
            raise TypeError("url must be a string.")

        url = url.strip()

        if not url:
            raise ValueError("Browser URL cannot be empty.")

        requested_pages = (
            self.max_pages
            if max_pages is None
            else int(max_pages)
        )

        if requested_pages < 1:
            raise ValueError("max_pages must be at least 1.")

        requested_pages = min(
            requested_pages,
            self.max_pages,
        )

        request = BrowserRequest(
            url=url,
            persona_id=persona_id,
            max_pages=requested_pages,
            allow_downloads=False,
            allow_uploads=False,
            metadata=dict(metadata or {}),
        )

        request.validate()

        return request

    def navigate(
        self,
        session_id: str,
        url: str,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> BrowserResult:
        """
        Prepare a navigation for an existing session.

        Actual navigation is delegated to an approved browser backend.
        """

        session = self.get_session(session_id)

        if session is None:
            return BrowserResult(
                success=False,
                request=BrowserRequest(url=url),
                error="Browser session does not exist.",
            )

        if not session.active:
            return BrowserResult(
                success=False,
                request=BrowserRequest(url=url),
                error="Browser session is not active.",
            )

        if session.pages_visited >= self.max_pages:
            return BrowserResult(
                success=False,
                request=BrowserRequest(url=url),
                session=session,
                error="Browser page limit has been reached.",
            )

        try:
            request = self.prepare_navigation(
                url=url,
                persona_id=session.persona_id,
                metadata=metadata,
            )
        except (TypeError, ValueError) as exc:
            return BrowserResult(
                success=False,
                request=BrowserRequest(url=str(url)),
                session=session,
                error=str(exc),
            )

        session.pages_visited += 1

        return BrowserResult(
            success=True,
            request=request,
            session=session,
        )

    def record_action(self, session_id: str) -> bool:
        """Record a bounded browser action."""

        session = self.get_session(session_id)

        if session is None or not session.active:
            return False

        if session.actions_performed >= self.max_actions:
            return False

        session.actions_performed += 1
        return True


PLUGIN = BrowserPlugin()
