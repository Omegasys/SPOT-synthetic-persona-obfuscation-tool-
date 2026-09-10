from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..audit.logger import AuditLogger
from .interface import PluginContext, SPOTPlugin
from .loader import PluginLoader
from .registry import PluginRegistry


@dataclass
class PluginPolicy:
    """Default-deny plugin capability policy."""

    allowed_capabilities: set[str] = field(default_factory=set)

    denied_capabilities: set[str] = field(
        default_factory=lambda: {
            "credentials",
            "personal_data",
            "qubes.rpc",
            "privileged",
            "raw_network",
            "filesystem_unrestricted",
            "process_unrestricted",
        }
    )

    allow_unknown_capabilities: bool = False

    def allows(self, capability: str) -> bool:
        """Check whether a capability is permitted."""
        if capability in self.denied_capabilities:
            return False

        if capability in self.allowed_capabilities:
            return True

        return self.allow_unknown_capabilities


class PluginManager:
    """Coordinates plugin loading, permissions, lifecycle, and events."""

    def __init__(
        self,
        registry: PluginRegistry | None = None,
        policy: PluginPolicy | None = None,
        audit: AuditLogger | None = None,
    ) -> None:
        self.registry = registry or PluginRegistry()
        self.policy = policy or PluginPolicy()
        self.audit = audit

        self.loader = PluginLoader(self.registry)

    def load_module(
        self,
        module_name: str,
    ) -> SPOTPlugin:
        """Load and register a plugin module."""
        plugin = self.loader.load_module(module_name)

        self._audit(
            "plugin_loaded",
            f"Plugin loaded: {plugin.metadata.id}",
        )

        return plugin

    def load_file(
        self,
        path: str,
    ) -> SPOTPlugin:
        """Load and register a plugin file."""
        plugin = self.loader.load_file(path)

        self._audit(
            "plugin_loaded",
            f"Plugin loaded: {plugin.metadata.id}",
        )

        return plugin

    def enable(
        self,
        plugin_id: str,
    ) -> bool:
        """Enable a plugin if its requested capabilities are permitted."""
        record = self.registry.require(plugin_id)
        metadata = record.plugin.metadata

        denied = [
            capability
            for capability in metadata.capabilities
            if not self.policy.allows(capability)
        ]

        if denied:
            self.registry.mark_error(
                plugin_id,
                "Denied capabilities: "
                + ", ".join(sorted(denied)),
            )

            self._audit(
                "plugin_rejected",
                f"Plugin rejected: {plugin_id}",
                metadata={
                    "denied_capabilities": sorted(denied),
                },
            )

            return False

        context = PluginContext(
            plugin_id=plugin_id,
            granted_capabilities=frozenset(
                metadata.capabilities
            ),
        )

        try:
            record.plugin.initialize(context)
            self.registry.mark_initialized(plugin_id)
            self.registry.enable(plugin_id)

        except Exception as exc:
            self.registry.mark_error(
                plugin_id,
                str(exc),
            )

            self._audit(
                "plugin_rejected",
                f"Plugin initialization failed: {plugin_id}",
            )

            return False

        self._audit(
            "plugin_enabled",
            f"Plugin enabled: {plugin_id}",
        )

        return True

    def disable(
        self,
        plugin_id: str,
    ) -> None:
        """Disable a plugin."""
        self.registry.disable(plugin_id)

        self._audit(
            "plugin_disabled",
            f"Plugin disabled: {plugin_id}",
        )

    def shutdown_all(self) -> None:
        """Shut down all plugins."""
        for record in list(self.registry.records()):
            if record.initialized:
                try:
                    record.plugin.shutdown()
                finally:
                    record.initialized = False

            record.enabled = False

    def broadcast(
        self,
        event: dict[str, Any],
    ) -> None:
        """
        Broadcast a sanitized event to enabled plugins.

        Plugin event delivery is best-effort and does not allow one
        plugin failure to stop SPOT itself.
        """
        for record in list(self.registry.records()):
            if not record.enabled or not record.initialized:
                continue

            try:
                record.plugin.on_event(dict(event))
            except Exception as exc:
                self.registry.mark_error(
                    record.plugin.metadata.id,
                    str(exc),
                )

                self._audit(
                    "plugin_error",
                    f"Plugin event handler failed: "
                    f"{record.plugin.metadata.id}",
                )

    def health(self) -> dict[str, bool]:
        """Return health status for enabled plugins."""
        result: dict[str, bool] = {}

        for plugin in self.registry.enabled():
            try:
                result[plugin.metadata.id] = (
                    plugin.health_check()
                )
            except Exception:
                result[plugin.metadata.id] = False

        return result

    def _audit(
        self,
        event_type: str,
        message: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Write an audit event when audit logging is available."""
        if self.audit is None:
            return

        self.audit.info(
            event_type,
            message,
            metadata=metadata or {},
        )
