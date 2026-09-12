"""Tests for the SPOT Linux platform plugin."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from spot.plugins.platforms.linux.plugin import (
    LinuxConfig,
    LinuxPathPolicy,
    LinuxPlugin,
    LinuxPluginStatus,
    LinuxSandbox,
)


def test_plugin_metadata() -> None:
    plugin = LinuxPlugin()

    assert plugin.metadata.plugin_id == "platform-linux"
    assert "platform.linux" in plugin.metadata.capabilities


def test_default_configuration_is_safe() -> None:
    config = LinuxConfig()

    assert config.enabled is False
    assert config.fail_closed is True
    assert config.allow_direct_network is False
    assert config.allow_root_operations is False
    assert config.allow_shell is False
    assert config.allow_arbitrary_commands is False
    assert config.prevent_dns_bypass is True


def test_unsafe_root_configuration_is_rejected() -> None:
    config = LinuxConfig(allow_root_operations=True)

    with pytest.raises(ValueError):
        config.validate()


def test_shell_configuration_is_rejected() -> None:
    config = LinuxConfig(allow_shell=True)

    with pytest.raises(ValueError):
        config.validate()


def test_arbitrary_command_configuration_is_rejected() -> None:
    config = LinuxConfig(allow_arbitrary_commands=True)

    with pytest.raises(ValueError):
        config.validate()


def test_required_sandbox_cannot_be_none() -> None:
    config = LinuxConfig(
        sandbox=LinuxSandbox.NONE,
        require_sandbox=True,
    )

    with pytest.raises(ValueError):
        config.validate()


def test_plugin_initializes_disabled_by_default() -> None:
    plugin = LinuxPlugin()

    plugin.initialize()

    assert plugin.status_value == LinuxPluginStatus.DISABLED


def test_linux_detection() -> None:
    plugin = LinuxPlugin()

    with patch("platform.system", return_value="Linux"):
        assert plugin.detect_linux() is True


def test_non_linux_is_rejected_when_linux_is_required() -> None:
    plugin = LinuxPlugin()

    plugin.initialize(
        {
            "enabled": True,
            "require_linux": True,
        }
    )

    with patch("platform.system", return_value="FreeBSD"):
        health = plugin.health_check()

    assert health.platform_ok is False


def test_emergency_stop_blocks_network() -> None:
    plugin = LinuxPlugin()

    plugin.initialize({"enabled": True})
    plugin.emergency_stop()

    assert plugin.status_value == LinuxPluginStatus.BLOCKED
    assert plugin.network_allowed() is False


def test_emergency_stop_can_be_reset() -> None:
    plugin = LinuxPlugin()

    plugin.initialize({"enabled": True})
    plugin.emergency_stop()

    assert plugin.status_value == LinuxPluginStatus.BLOCKED

    plugin.reset_emergency_stop()

    assert plugin.status_value == LinuxPluginStatus.CONFIGURED


def test_root_operations_are_never_allowed() -> None:
    plugin = LinuxPlugin()

    assert plugin.can_use_root() is False


def test_shell_is_never_allowed() -> None:
    plugin = LinuxPlugin()

    assert plugin.can_use_shell() is False


def test_arbitrary_commands_are_never_allowed() -> None:
    plugin = LinuxPlugin()

    assert plugin.can_execute(["echo", "test"]) is False


def test_path_policy_allows_spot_paths() -> None:
    policy = LinuxPathPolicy(
        allowed=("/var/lib/spot",),
        denied=("/root",),
    )

    assert policy.is_allowed("/var/lib/spot/personas/example") is True


def test_path_policy_denies_home() -> None:
    policy = LinuxPathPolicy(
        allowed=("/var/lib/spot",),
        denied=("/home",),
    )

    assert policy.is_allowed("/home/example") is False


def test_path_policy_denies_root() -> None:
    policy = LinuxPathPolicy(
        allowed=("/var/lib/spot",),
        denied=("/root",),
    )

    assert policy.is_allowed("/root/.ssh") is False


def test_path_policy_denies_sensitive_system_file() -> None:
    policy = LinuxPathPolicy(
        allowed=("/etc/spot",),
        denied=("/etc/shadow",),
    )

    assert policy.is_allowed(Path("/etc/shadow")) is False


def test_sandbox_none_without_requirement_is_available() -> None:
    plugin = LinuxPlugin()

    plugin.initialize(
        {
            "sandbox": "none",
            "require_sandbox": False,
        }
    )

    status = plugin.sandbox_status()

    assert status.mechanism == LinuxSandbox.NONE
    assert status.available is True


def test_systemd_detection_is_noninvasive() -> None:
    plugin = LinuxPlugin()

    with patch(
        "shutil.which",
        return_value="/usr/bin/systemctl",
    ):
        assert plugin.systemd_available() is True


def test_bubblewrap_detection_is_noninvasive() -> None:
    plugin = LinuxPlugin()

    plugin.initialize(
        {
            "sandbox": "bubblewrap",
            "require_sandbox": True,
        }
    )

    with patch(
        "shutil.which",
        return_value="/usr/bin/bwrap",
    ):
        status = plugin.sandbox_status()

    assert status.available is True


def test_network_is_blocked_when_plugin_disabled() -> None:
    plugin = LinuxPlugin()

    plugin.initialize({"enabled": False})

    assert plugin.network_allowed() is False


def test_network_allowed_when_enabled_and_healthy() -> None:
    plugin = LinuxPlugin()

    plugin.initialize(
        {
            "enabled": True,
            "require_systemd": False,
            "sandbox": "none",
            "require_sandbox": False,
        }
    )

    with patch("platform.system", return_value="Linux"):
        assert plugin.network_allowed() is True


def test_status_does_not_expose_credentials() -> None:
    plugin = LinuxPlugin()

    plugin.initialize()

    status = plugin.status()

    assert "password" not in status
    assert "token" not in status
    assert "credential" not in status


def test_status_reports_security_restrictions() -> None:
    plugin = LinuxPlugin()

    plugin.initialize()

    status = plugin.status()

    assert status["root_operations"] is False
    assert status["shell_access"] is False
    assert status["arbitrary_commands"] is False


def test_fail_closed_health_when_required_sandbox_missing() -> None:
    plugin = LinuxPlugin()

    plugin.initialize(
        {
            "enabled": True,
            "require_sandbox": True,
            "sandbox": "bubblewrap",
        }
    )

    with patch(
        "shutil.which",
        return_value=None,
    ):
        health = plugin.health_check()

    assert health.sandbox_available is False
    assert health.healthy is False


def test_plugin_can_start_when_requirements_are_available() -> None:
    plugin = LinuxPlugin()

    plugin.initialize(
        {
            "enabled": True,
            "require_systemd": False,
            "sandbox": "none",
            "require_sandbox": False,
        }
    )

    with patch("platform.system", return_value="Linux"):
        plugin.start()

    assert plugin.status_value == LinuxPluginStatus.AVAILABLE


def test_plugin_does_not_execute_commands() -> None:
    plugin = LinuxPlugin()

    commands = [
        ["systemctl", "start", "something"],
        ["qvm", "start", "something"],
        ["sh", "-c", "anything"],
    ]

    for command in commands:
        assert plugin.can_execute(command) is False


def test_path_policy_does_not_use_string_prefix_bypass() -> None:
    policy = LinuxPathPolicy(
        allowed=("/var/lib/spot",),
        denied=(),
    )

    assert policy.is_allowed("/var/lib/spot-other") is False


def test_stop_returns_to_configured_state() -> None:
    plugin = LinuxPlugin()

    plugin.initialize({"enabled": True})
    plugin.stop()

    assert plugin.status_value == LinuxPluginStatus.CONFIGURED
