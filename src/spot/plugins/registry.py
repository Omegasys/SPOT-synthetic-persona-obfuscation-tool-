from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

from .interface import SPOTPlugin


@dataclass
class PluginRecord:
    """Registered plugin state."""

    plugin: SPOTPlugin
    enabled: bool = False
    initialized: bool = False
    error: str | None = None


class PluginRegistry:
    """Registry of installed and loaded plugins."""

    def __init__(self) -> None:
        self._plugins: dict[str, PluginRecord] = {}

    def register(
        self,
        plugin: SPOTPlugin,
    ) -> None:
        """Register a plugin."""
        plugin.metadata.validate()

        plugin_id = plugin.metadata.id

        if plugin_id in self._plugins:
            raise ValueError(
                f"Plugin already registered: {plugin_id}"
            )

        self._plugins[plugin_id] = PluginRecord(
            plugin=plugin
        )

    def unregister(self, plugin_id: str) -> None:
        """Remove a plugin from the registry."""
        record = self.require(plugin_id)

        if record.initialized:
            record.plugin.shutdown()

        del self._plugins[plugin_id]

    def get(
        self,
        plugin_id: str,
    ) -> SPOTPlugin | None:
        """Return a plugin if registered."""
        record = self._plugins.get(plugin_id)

        return record.plugin if record else None

    def require(
        self,
        plugin_id: str,
    ) -> PluginRecord:
        """Return a plugin record or raise an error."""
        try:
            return self._plugins[plugin_id]
        except KeyError as exc:
            raise KeyError(
                f"Unknown plugin: {plugin_id}"
            ) from exc

    def enable(self, plugin_id: str) -> None:
        """Enable a registered plugin."""
        self.require(plugin_id).enabled = True

    def disable(self, plugin_id: str) -> None:
        """Disable a plugin."""
        record = self.require(plugin_id)

        if record.initialized:
            record.plugin.shutdown()
            record.initialized = False

        record.enabled = False

    def all(self) -> list[SPOTPlugin]:
        """Return all registered plugins."""
        return [
            record.plugin
            for record in self._plugins.values()
        ]

    def enabled(self) -> list[SPOTPlugin]:
        """Return enabled plugins."""
        return [
            record.plugin
            for record in self._plugins.values()
            if record.enabled
        ]

    def records(self) -> Iterator[PluginRecord]:
        """Iterate over plugin records."""
        return iter(self._plugins.values())

    def mark_initialized(
        self,
        plugin_id: str,
        initialized: bool = True,
    ) -> None:
        """Update initialization state."""
        self.require(plugin_id).initialized = initialized

    def mark_error(
        self,
        plugin_id: str,
        error: str,
    ) -> None:
        """Record a plugin error and disable it."""
        record = self.require(plugin_id)

        record.error = error
        record.enabled = False
        record.initialized = False

    def clear_error(self, plugin_id: str) -> None:
        """Clear a plugin error."""
        self.require(plugin_id).error = None

    def contains(self, plugin_id: str) -> bool:
        """Check whether a plugin is registered."""
        return plugin_id in self._plugins

    def count(self) -> int:
        """Return registered plugin count."""
        return len(self._plugins)
