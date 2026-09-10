from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PluginMetadata:
    """Describes a SPOT plugin."""

    id: str
    name: str
    version: str
    description: str = ""
    author: str = ""
    api_version: str = "1"
    capabilities: frozenset[str] = frozenset()

    def validate(self) -> None:
        """Validate plugin metadata."""
        if not self.id:
            raise ValueError("Plugin id cannot be empty.")

        if not self.name:
            raise ValueError("Plugin name cannot be empty.")

        if not self.version:
            raise ValueError("Plugin version cannot be empty.")

        if not self.api_version:
            raise ValueError("Plugin API version cannot be empty.")


@dataclass
class PluginContext:
    """Restricted context provided to plugins."""

    plugin_id: str
    granted_capabilities: frozenset[str] = frozenset()
    metadata: dict[str, Any] = field(default_factory=dict)

    def has_capability(self, capability: str) -> bool:
        """Check whether a plugin has a capability."""
        return capability in self.granted_capabilities


class SPOTPlugin(ABC):
    """Base interface implemented by SPOT plugins."""

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        raise NotImplementedError

    def initialize(
        self,
        context: PluginContext,
    ) -> None:
        """Initialize the plugin."""
        del context

    def shutdown(self) -> None:
        """Shut down the plugin."""
        return None

    def health_check(self) -> bool:
        """Return whether the plugin is healthy."""
        return True

    def on_event(
        self,
        event: dict[str, Any],
    ) -> None:
        """Receive a sanitized SPOT event."""
        del event
