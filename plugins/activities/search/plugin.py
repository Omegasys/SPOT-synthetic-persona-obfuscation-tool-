from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional

from spot.plugins.interface import PluginMetadata, SPOTPlugin


@dataclass
class SearchRequest:
    """A bounded synthetic search request."""

    query: str
    persona_id: Optional[str] = None
    max_results: int = 10
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.query or not self.query.strip():
            raise ValueError("Search query cannot be empty.")

        if len(self.query) > 500:
            raise ValueError("Search query is too long.")

        if self.max_results < 1:
            raise ValueError("max_results must be at least 1.")

        if self.max_results > 100:
            raise ValueError("max_results exceeds the plugin safety limit.")


@dataclass
class SearchResult:
    """Provider-neutral result returned by the plugin."""

    success: bool
    request: SearchRequest
    results: list[dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None


class SearchPlugin(SPOTPlugin):
    """
    SPOT synthetic search activity plugin.

    This plugin prepares bounded search activity. Actual network access
    should be performed by an approved SPOT networking/provider backend.
    """

    metadata = PluginMetadata(
        id="activity-search",
        name="Search Activity Plugin",
        version="0.1.0",
        description=(
            "Provides bounded, provider-neutral synthetic search activity."
        ),
    )

    def __init__(
        self,
        max_results: int = 10,
        max_query_length: int = 500,
    ) -> None:
        self.max_results = max_results
        self.max_query_length = max_query_length
        self._initialized = False
        self._running = False

    def initialize(self, context: Any) -> bool:
        """
        Initialize the plugin.

        The context is intentionally treated as an opaque SPOT plugin
        context so the plugin does not depend on unrestricted host access.
        """
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
        """Return whether the plugin is initialized and operational."""
        return self._initialized and self._running

    def prepare_search(
        self,
        query: str,
        persona_id: Optional[str] = None,
        max_results: Optional[int] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> SearchRequest:
        """
        Prepare a bounded search request.

        This method does not perform network access.
        """

        if not isinstance(query, str):
            raise TypeError("query must be a string.")

        query = query.strip()

        if not query:
            raise ValueError("Search query cannot be empty.")

        if len(query) > self.max_query_length:
            raise ValueError("Search query is too long.")

        requested_results = (
            self.max_results
            if max_results is None
            else int(max_results)
        )

        if requested_results < 1:
            raise ValueError("max_results must be at least 1.")

        requested_results = min(
            requested_results,
            self.max_results,
        )

        request = SearchRequest(
            query=query,
            persona_id=persona_id,
            max_results=requested_results,
            metadata=dict(metadata or {}),
        )

        request.validate()

        return request

    def execute(
        self,
        query: str,
        persona_id: Optional[str] = None,
        max_results: Optional[int] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> SearchResult:
        """
        Prepare a search activity.

        Actual provider/network execution is intentionally not performed
        by this generic plugin.
        """

        if not self._running:
            return SearchResult(
                success=False,
                request=SearchRequest(query=query),
                error="Search plugin is not running.",
            )

        try:
            request = self.prepare_search(
                query=query,
                persona_id=persona_id,
                max_results=max_results,
                metadata=metadata,
            )
        except (TypeError, ValueError) as exc:
            return SearchResult(
                success=False,
                request=SearchRequest(query=str(query)),
                error=str(exc),
            )

        return SearchResult(
            success=True,
            request=request,
            results=[],
        )


PLUGIN = SearchPlugin()
