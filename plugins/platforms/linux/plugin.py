"""Linux platform integration for SPOT.

This module provides a restricted Linux-native platform backend.

It intentionally does not perform unrestricted privileged operations.
"""

from __future__ import annotations

import os
import platform
import shutil
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from spot.plugins.interface import PluginMetadata, SPOTPlugin


class LinuxPluginStatus(str, Enum):
    """Current Linux plugin state."""

    DISABLED = "disabled"
    CONFIGURED = "configured"
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    BLOCKED = "blocked"
    ERROR = "error"


class LinuxSandbox(str, Enum):
    """Supported Linux sandbox mechanisms."""

    NONE = "none"
    SYSTEMD = "systemd"
    BUBBLEWRAP = "bubblewrap"
    APPARMOR = "apparmor"
    SELINUX = "selinux"
    NAMESPACE = "namespace"


@dataclass
class LinuxConfig:
    """Configuration for the Linux platform plugin."""

    enabled: bool = False
    fail_closed: bool = True

    require_linux: bool = True
    require_systemd: bool = False

    sandbox: LinuxSandbox = LinuxSandbox.SYSTEMD
    require_sandbox: bool = False

    allow_direct_network: bool = False
    prevent_dns_bypass: bool = True

    allow_root_operations: bool = False
    allow_shell: bool = False
    allow_arbitrary_commands: bool = False

    config_directory: str = "/etc/spot"
    state_directory: str = "/var/lib/spot"
    runtime_directory: str = "/run/spot"
    log_directory: str = "/var/log/spot"

    allowed_paths: list[str] = field(
        default_factory=lambda: [
            "/etc/spot",
            "/var/lib/spot",
            "/run/spot",
            "/var/log/spot",
        ]
    )

    denied_paths: list[str] = field(
        default_factory=lambda: [
            "/root",
            "/home",
            "/etc/shadow",
            "/etc/gshadow",
            "/etc/passwd",
            "/etc/sudoers",
            "/etc/ssh",
            "/var/lib/private",
        ]
    )

    def validate(self) -> None:
        """Validate the configuration."""

        if not self.config_directory:
            raise ValueError("config_directory must not be empty")

        if not self.state_directory:
            raise ValueError("state_directory must not be empty")

        if not self.runtime_directory:
            raise ValueError("runtime_directory must not be empty")

        if not self.log_directory:
            raise ValueError("log_directory must not be empty")

        if self.require_sandbox and self.sandbox == LinuxSandbox.NONE:
            raise ValueError("require_sandbox cannot be used with sandbox=none")

        if self.allow_root_operations:
            raise ValueError(
                "unrestricted root operations are not supported by the Linux plugin"
            )

        if self.allow_shell:
            raise ValueError(
                "shell access is not supported by the Linux plugin"
            )

        if self.allow_arbitrary_commands:
            raise ValueError(
                "arbitrary command execution is not supported by the Linux plugin"
            )


@dataclass(frozen=True)
class LinuxPathPolicy:
    """Policy describing whether a path is available to SPOT."""

    allowed: tuple[str, ...] = ()
    denied: tuple[str, ...] = ()

    def is_allowed(self, path: str | Path) -> bool:
        """Return whether a path is permitted by the policy."""

        candidate = Path(path).resolve(strict=False)

        for denied_path in self.denied:
            denied = Path(denied_path).resolve(strict=False)

            if candidate == denied or denied in candidate.parents:
                return False

        for allowed_path in self.allowed:
            allowed = Path(allowed_path).resolve(strict=False)

            if candidate == allowed or allowed in candidate.parents:
                return True

        return False


@dataclass
class LinuxSandboxStatus:
    """Status information for the selected sandbox."""

    mechanism: LinuxSandbox
    available: bool
    required: bool
    reason: str = ""


@dataclass
class LinuxHealth:
    """Linux platform health information."""

    platform_ok: bool
    systemd_available: bool
    sandbox_available: bool
    network_allowed: bool
    emergency_stop: bool
    reason: str = ""

    @property
    def healthy(self) -> bool:
        """Return whether the platform is healthy."""

        if self.emergency_stop:
            return False

        return (
            self.platform_ok
            and self.systemd_available
            and self.sandbox_available
            and self.network_allowed
        )


class LinuxPlugin(SPOTPlugin):
    """Restricted Linux platform integration."""

    metadata = PluginMetadata(
        plugin_id="platform-linux",
        name="SPOT Linux Platform",
        version="0.1.0",
        description="Restricted Linux-native platform integration.",
        author="SPOT Project",
        capabilities={
            "platform.linux",
            "systemd",
            "sandbox",
            "filesystem-policy",
            "network-policy",
        },
        permissions={
            "filesystem.scoped",
            "platform.detect",
        },
    )

    def __init__(self) -> None:
        self.config = LinuxConfig()
        self.status_value = LinuxPluginStatus.DISABLED
        self._emergency_stop = False
        self._initialized = False

    def initialize(self, config: dict[str, Any] | None = None) -> None:
        """Initialize the plugin from a configuration dictionary."""

        if config:
            self._load_config(config)

        self.config.validate()

        if self.config.require_linux and platform.system() != "Linux":
            self.status_value = LinuxPluginStatus.UNAVAILABLE
            self._initialized = True

            if self.config.fail_closed:
                return

        self.status_value = (
            LinuxPluginStatus.CONFIGURED
            if self.config.enabled
            else LinuxPluginStatus.DISABLED
        )

        self._initialized = True

    def _load_config(self, config: dict[str, Any]) -> None:
        """Load supported configuration fields."""

        for key in (
            "enabled",
            "fail_closed",
            "require_linux",
            "require_systemd",
            "require_sandbox",
            "allow_direct_network",
            "prevent_dns_bypass",
            "allow_root_operations",
            "allow_shell",
            "allow_arbitrary_commands",
            "config_directory",
            "state_directory",
            "runtime_directory",
            "log_directory",
            "allowed_paths",
            "denied_paths",
        ):
            if key in config:
                setattr(self.config, key, config[key])

        if "sandbox" in config:
            self.config.sandbox = LinuxSandbox(config["sandbox"])

    def start(self) -> None:
        """Start the platform integration."""

        if not self._initialized:
            self.initialize()

        if self._emergency_stop:
            self.status_value = LinuxPluginStatus.BLOCKED
            return

        if not self.config.enabled:
            self.status_value = LinuxPluginStatus.DISABLED
            return

        health = self.health_check()

        if not health.healthy:
            self.status_value = LinuxPluginStatus.UNAVAILABLE
            return

        self.status_value = LinuxPluginStatus.AVAILABLE

    def stop(self) -> None:
        """Stop the platform integration."""

        self.status_value = (
            LinuxPluginStatus.CONFIGURED
            if self.config.enabled
            else LinuxPluginStatus.DISABLED
        )

    def health_check(self) -> LinuxHealth:
        """Perform a non-invasive Linux platform health check."""

        platform_ok = (
            platform.system() == "Linux"
            if self.config.require_linux
            else True
        )

        systemd_available = self.systemd_available()

        if self.config.require_systemd:
            systemd_ok = systemd_available
        else:
            systemd_ok = True

        sandbox = self.sandbox_status()

        sandbox_ok = sandbox.available or not self.config.require_sandbox

        network_allowed = (
            self.config.allow_direct_network
            if self.config.allow_direct_network
            else True
        )

        reason = ""

        if not platform_ok:
            reason = "Linux platform is required"

        elif not systemd_ok:
            reason = "systemd is required but unavailable"

        elif not sandbox_ok:
            reason = "required sandbox mechanism is unavailable"

        elif self._emergency_stop:
            reason = "emergency stop is active"

        return LinuxHealth(
            platform_ok=platform_ok,
            systemd_available=systemd_available,
            sandbox_available=sandbox.available,
            network_allowed=network_allowed,
            emergency_stop=self._emergency_stop,
            reason=reason,
        )

    @staticmethod
    def detect_linux() -> bool:
        """Return whether the current platform is Linux."""

        return platform.system() == "Linux"

    @staticmethod
    def systemd_available() -> bool:
        """Return whether systemd tooling appears to be installed."""

        return shutil.which("systemctl") is not None

    def sandbox_status(self) -> LinuxSandboxStatus:
        """Determine whether the configured sandbox mechanism is available."""

        mechanism = self.config.sandbox

        if mechanism == LinuxSandbox.NONE:
            return LinuxSandboxStatus(
                mechanism=mechanism,
                available=not self.config.require_sandbox,
                required=self.config.require_sandbox,
                reason="sandboxing disabled",
            )

        if mechanism == LinuxSandbox.SYSTEMD:
            available = self.systemd_available()

        elif mechanism == LinuxSandbox.BUBBLEWRAP:
            available = shutil.which("bwrap") is not None

        elif mechanism == LinuxSandbox.APPARMOR:
            available = Path("/sys/kernel/security/apparmor").exists()

        elif mechanism == LinuxSandbox.SELINUX:
            available = Path("/sys/fs/selinux").exists()

        elif mechanism == LinuxSandbox.NAMESPACE:
            available = Path("/proc/self/ns").exists()

        else:
            available = False

        return LinuxSandboxStatus(
            mechanism=mechanism,
            available=available,
            required=self.config.require_sandbox,
            reason="" if available else "sandbox mechanism unavailable",
        )

    def path_policy(self) -> LinuxPathPolicy:
        """Return the configured filesystem policy."""

        return LinuxPathPolicy(
            allowed=tuple(self.config.allowed_paths),
            denied=tuple(self.config.denied_paths),
        )

    def path_allowed(self, path: str | Path) -> bool:
        """Check a path against the restricted filesystem policy."""

        return self.path_policy().is_allowed(path)

    def network_allowed(self) -> bool:
        """Return whether Linux integration permits network activity."""

        if self._emergency_stop:
            return False

        if not self.config.enabled:
            return False

        health = self.health_check()

        if self.config.fail_closed and not health.platform_ok:
            return False

        return health.network_allowed

    def can_execute(self, command: list[str]) -> bool:
        """Return whether a command could be accepted.

        The Linux plugin intentionally does not execute arbitrary commands.
        This method exists to make that policy explicit.
        """

        del command
        return False

    def can_use_root(self) -> bool:
        """Return whether unrestricted root operations are permitted."""

        return False

    def can_use_shell(self) -> bool:
        """Return whether shell access is permitted."""

        return False

    def emergency_stop(self) -> None:
        """Block new Linux-integrated SPOT activity."""

        self._emergency_stop = True
        self.status_value = LinuxPluginStatus.BLOCKED

    def reset_emergency_stop(self) -> None:
        """Clear the emergency stop state."""

        self._emergency_stop = False

        if self.config.enabled:
            self.status_value = LinuxPluginStatus.CONFIGURED
        else:
            self.status_value = LinuxPluginStatus.DISABLED

    def status(self) -> dict[str, Any]:
        """Return a safe status summary."""

        health = self.health_check()
        sandbox = self.sandbox_status()

        return {
            "plugin": self.metadata.plugin_id,
            "status": self.status_value.value,
            "enabled": self.config.enabled,
            "initialized": self._initialized,
            "linux": self.detect_linux(),
            "systemd": self.systemd_available(),
            "sandbox": {
                "mechanism": sandbox.mechanism.value,
                "available": sandbox.available,
                "required": sandbox.required,
            },
            "network_allowed": self.network_allowed(),
            "emergency_stop": self._emergency_stop,
            "health": health.healthy,
            "health_reason": health.reason,
            "root_operations": False,
            "shell_access": False,
            "arbitrary_commands": False,
        }


PLUGIN = LinuxPlugin()
