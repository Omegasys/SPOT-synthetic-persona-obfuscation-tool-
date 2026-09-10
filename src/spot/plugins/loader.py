from __future__ import annotations

import importlib
import importlib.util
from pathlib import Path
from types import ModuleType

from .interface import SPOTPlugin
from .registry import PluginRegistry


class PluginLoader:
    """
    Loads SPOT plugins from explicitly approved Python modules.

    Loading code is inherently privileged from a Python-process
    perspective, so callers should only provide trusted plugin paths.
    The loader itself does not grant plugin capabilities.
    """

    PLUGIN_ATTRIBUTE = "PLUGIN"

    def __init__(
        self,
        registry: PluginRegistry,
    ) -> None:
        self.registry = registry

    def load_module(
        self,
        module_name: str,
    ) -> SPOTPlugin:
        """Load a plugin from an importable Python module."""
        if not module_name:
            raise ValueError("module_name cannot be empty.")

        module = importlib.import_module(module_name)

        return self._register_from_module(module)

    def load_file(
        self,
        path: str | Path,
    ) -> SPOTPlugin:
        """Load a plugin from an explicitly selected Python file."""
        plugin_path = Path(path).expanduser().resolve()

        if not plugin_path.exists():
            raise FileNotFoundError(
                f"Plugin file does not exist: {plugin_path}"
            )

        if plugin_path.suffix != ".py":
            raise ValueError(
                "Plugin files must use the .py extension."
            )

        module_name = (
            f"spot_external_plugin_"
            f"{plugin_path.stem}"
        )

        spec = importlib.util.spec_from_file_location(
            module_name,
            plugin_path,
        )

        if spec is None or spec.loader is None:
            raise ImportError(
                f"Unable to load plugin: {plugin_path}"
            )

        module = importlib.util.module_from_spec(spec)

        spec.loader.exec_module(module)

        return self._register_from_module(module)

    def _register_from_module(
        self,
        module: ModuleType,
    ) -> SPOTPlugin:
        """Extract and register the plugin object."""
        plugin = getattr(
            module,
            self.PLUGIN_ATTRIBUTE,
            None,
        )

        if not isinstance(plugin, SPOTPlugin):
            raise TypeError(
                "Plugin module must expose a SPOTPlugin "
                "instance named PLUGIN."
            )

        self.registry.register(plugin)

        return plugin
