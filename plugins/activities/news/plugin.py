from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional

from spot.plugins.interface import PluginMetadata, SPOTPlugin


@dataclass
class NewsRequest:
    """A bounded synthetic news activity request."""

    topic: str
    persona_id: Optional[str] = None
    max_articles: int = 5
    max_sources: int = 3
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.topic or not self.topic.strip():
            raise ValueError("News topic cannot be empty.")

        if len(self.topic) > 200:
            raise ValueError("News topic is too long.")

        if self.max_articles < 1:
            raise ValueError("max_articles must be at least 1.")

        if self.max_articles > 50:
            raise ValueError(
                "max_articles exceeds the plugin safety limit."
            )

        if self.max_sources < 1:
            raise ValueError("max_sources must be at least 1.")

        if self.max_sources > 20:
            raise ValueError(
                "max_sources exceeds the plugin safety limit."
            )


@dataclass
class NewsArticle:
    """Provider-neutral representation of a news article."""

    title: str
    source: Optional[str] = None
    url: Optional[str] = None
    topic: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class NewsResult:
    """Provider-neutral result returned by the news plugin."""

    success: bool
    request: NewsRequest
    articles: list[NewsArticle] = field(default_factory=list)
    error: Optional[str] = None


class NewsPlugin(SPOTPlugin):
    """
    SPOT synthetic news activity plugin.

    The plugin prepares bounded news activity. Actual network retrieval
    should be delegated to an approved SPOT provider/network backend.
    """

    metadata = PluginMetadata(
        id="activity-news",
        name="News Activity Plugin",
        version="0.1.0",
        description=(
            "Provides bounded, provider-neutral synthetic news activity."
        ),
    )

    def __init__(
        self,
        max_articles: int = 5,
        max_sources: int = 3,
        max_topic_length: int = 200,
    ) -> None:
        self.max_articles = max_articles
        self.max_sources = max_sources
        self.max_topic_length = max_topic_length

        self._initialized = False
        self._running = False

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
        """Stop the plugin."""
        self._running = False
        return True

    def health_check(self) -> bool:
        """Return whether the plugin is operational."""
        return self._initialized and self._running

    def prepare_news(
        self,
        topic: str,
        persona_id: Optional[str] = None,
        max_articles: Optional[int] = None,
        max_sources: Optional[int] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> NewsRequest:
        """Prepare a bounded synthetic news request."""

        if not isinstance(topic, str):
            raise TypeError("topic must be a string.")

        topic = topic.strip()

        if not topic:
            raise ValueError("News topic cannot be empty.")

        if len(topic) > self.max_topic_length:
            raise ValueError("News topic is too long.")

        requested_articles = (
            self.max_articles
            if max_articles is None
            else int(max_articles)
        )

        requested_sources = (
            self.max_sources
            if max_sources is None
            else int(max_sources)
        )

        if requested_articles < 1:
            raise ValueError("max_articles must be at least 1.")

        if requested_sources < 1:
            raise ValueError("max_sources must be at least 1.")

        requested_articles = min(
            requested_articles,
            self.max_articles,
        )

        requested_sources = min(
            requested_sources,
            self.max_sources,
        )

        request = NewsRequest(
            topic=topic,
            persona_id=persona_id,
            max_articles=requested_articles,
            max_sources=requested_sources,
            metadata=dict(metadata or {}),
        )

        request.validate()

        return request

    def execute(
        self,
        topic: str,
        persona_id: Optional[str] = None,
        max_articles: Optional[int] = None,
        max_sources: Optional[int] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> NewsResult:
        """
        Prepare a news activity request.

        Actual external retrieval is intentionally not performed by this
        provider-neutral plugin.
        """

        if not self._running:
            return NewsResult(
                success=False,
                request=NewsRequest(topic=topic),
                error="News plugin is not running.",
            )

        try:
            request = self.prepare_news(
                topic=topic,
                persona_id=persona_id,
                max_articles=max_articles,
                max_sources=max_sources,
                metadata=metadata,
            )
        except (TypeError, ValueError) as exc:
            return NewsResult(
                success=False,
                request=NewsRequest(topic=str(topic)),
                error=str(exc),
            )

        return NewsResult(
            success=True,
            request=request,
            articles=[],
        )


PLUGIN = NewsPlugin()
