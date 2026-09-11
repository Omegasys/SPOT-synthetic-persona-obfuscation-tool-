from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Optional
from urllib.parse import urlparse

from spot.plugins.interface import PluginMetadata, SPOTPlugin


class MediaType(str, Enum):
    """Supported synthetic media activity types."""

    VIDEO = "video"
    AUDIO = "audio"
    MUSIC = "music"
    PODCAST = "podcast"
    IMAGE = "image"
    STREAM = "stream"


@dataclass
class MediaRequest:
    """A bounded synthetic media activity request."""

    media_type: MediaType
    target: str
    persona_id: Optional[str] = None
    duration_seconds: int = 300
    max_items: int = 5
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.target or not self.target.strip():
            raise ValueError("Media target cannot be empty.")

        if len(self.target) > 2000:
            raise ValueError("Media target is too long.")

        if self.duration_seconds < 1:
            raise ValueError(
                "duration_seconds must be at least 1."
            )

        if self.duration_seconds > 3600:
            raise ValueError(
                "duration_seconds exceeds the plugin safety limit."
            )

        if self.max_items < 1:
            raise ValueError("max_items must be at least 1.")

        if self.max_items > 50:
            raise ValueError(
                "max_items exceeds the plugin safety limit."
            )


@dataclass
class MediaItem:
    """Provider-neutral representation of a media item."""

    title: str
    media_type: MediaType
    source: Optional[str] = None
    url: Optional[str] = None
    duration_seconds: Optional[int] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MediaResult:
    """Result of a media activity request."""

    success: bool
    request: MediaRequest
    items: list[MediaItem] = field(default_factory=list)
    error: Optional[str] = None


class MediaPlugin(SPOTPlugin):
    """
    SPOT synthetic media activity plugin.

    This plugin prepares bounded media activity. Actual retrieval or
    playback is delegated to an approved SPOT provider/backend.
    """

    metadata = PluginMetadata(
        id="activity-media",
        name="Media Activity Plugin",
        version="0.1.0",
        description=(
            "Provides bounded, provider-neutral synthetic media activity."
        ),
    )

    def __init__(
        self,
        max_duration_seconds: int = 3600,
        max_items: int = 5,
        max_target_length: int = 2000,
    ) -> None:
        self.max_duration_seconds = max_duration_seconds
        self.max_items = max_items
        self.max_target_length = max_target_length

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

    def prepare_media(
        self,
        media_type: MediaType | str,
        target: str,
        persona_id: Optional[str] = None,
        duration_seconds: Optional[int] = None,
        max_items: Optional[int] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> MediaRequest:
        """Prepare a bounded synthetic media request."""

        if isinstance(media_type, str):
            try:
                media_type = MediaType(media_type.lower())
            except ValueError as exc:
                raise ValueError(
                    f"Unsupported media type: {media_type}"
                ) from exc

        if not isinstance(target, str):
            raise TypeError("target must be a string.")

        target = target.strip()

        if not target:
            raise ValueError("Media target cannot be empty.")

        if len(target) > self.max_target_length:
            raise ValueError("Media target is too long.")

        requested_duration = (
            300
            if duration_seconds is None
            else int(duration_seconds)
        )

        requested_items = (
            self.max_items
            if max_items is None
            else int(max_items)
        )

        if requested_duration < 1:
            raise ValueError(
                "duration_seconds must be at least 1."
            )

        if requested_items < 1:
            raise ValueError(
                "max_items must be at least 1."
            )

        requested_duration = min(
            requested_duration,
            self.max_duration_seconds,
        )

        requested_items = min(
            requested_items,
            self.max_items,
        )

        request = MediaRequest(
            media_type=media_type,
            target=target,
            persona_id=persona_id,
            duration_seconds=requested_duration,
            max_items=requested_items,
            metadata=dict(metadata or {}),
        )

        request.validate()

        return request

    def execute(
        self,
        media_type: MediaType | str,
        target: str,
        persona_id: Optional[str] = None,
        duration_seconds: Optional[int] = None,
        max_items: Optional[int] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> MediaResult:
        """
        Prepare media activity.

        Actual external retrieval or playback is intentionally not
        performed by this provider-neutral implementation.
        """

        try:
            request = self.prepare_media(
                media_type=media_type,
                target=target,
                persona_id=persona_id,
                duration_seconds=duration_seconds,
                max_items=max_items,
                metadata=metadata,
            )
        except (TypeError, ValueError) as exc:
            fallback_type = (
                MediaType.VIDEO
                if not isinstance(media_type, MediaType)
                else media_type
            )

            return MediaResult(
                success=False,
                request=MediaRequest(
                    media_type=fallback_type,
                    target=str(target),
                ),
                error=str(exc),
            )

        if not self._running:
            return MediaResult(
                success=False,
                request=request,
                error="Media plugin is not running.",
            )

        return MediaResult(
            success=True,
            request=request,
            items=[],
        )


PLUGIN = MediaPlugin()
