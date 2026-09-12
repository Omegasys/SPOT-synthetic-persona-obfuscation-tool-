from __future__ import annotations

import shutil

import pytest

from plugins.platforms.qubes.plugin import (
    QubeAssignment,
    QubeType,
    QubesNetworkMode,
    QubesPlugin,
    QubesPluginStatus,
    QubesRPCPolicy,
)


class DummyContext:
    """Minimal plugin context for offline tests."""


def make_plugin(
    assignments=None,
) -> QubesPlugin:
    """Create an initialized and started Qubes plugin."""

    plugin = QubesPlugin(
        assignments=assignments,
    )

    assert plugin.initialize(DummyContext()) is True
    assert plugin.start() is True

    return plugin


def test_metadata() -> None:
    assert QubesPlugin.metadata.id == "platform-qubes"
    assert QubesPlugin.metadata.name == "Qubes Platform Plugin"
    assert QubesPlugin.metadata.version == "0.1.0"


def test_default_security_policy() -> None:
    plugin = QubesPlugin()

    assert plugin.allow_direct_network is False
    assert plugin.require_whonix is True
    assert plugin.fail_closed is True

    assert plugin.rpc_policy.allow_dom0 is False
    assert plugin.rpc_policy.allow_arbitrary_commands is False
    assert plugin.rpc_policy.allow_shell is False


def test_plugin_lifecycle() -> None:
    plugin = QubesPlugin()

    assert plugin.status == QubesPluginStatus.UNAVAILABLE

    assert plugin.initialize(DummyContext()) is True
    assert plugin.status == QubesPluginStatus.CONFIGURED

    assert plugin.start() is True
    assert plugin.status == QubesPluginStatus.AVAILABLE
    assert plugin.health_check() is True

    assert plugin.stop() is True
    assert plugin.health_check() is False


def test_direct_network_with_fail_closed_is_rejected() -> None:
    plugin = QubesPlugin(
        fail_closed=True,
        allow_direct_network=True,
    )

    assert plugin.initialize(DummyContext()) is False


def test_assignment_validation() -> None:
    assignment = QubeAssignment(
        persona_id="alex",
        qube_name="spot-persona-01",
        qube_type=QubeType.APPVM,
        network_mode=QubesNetworkMode.WHONIX,
        network_qube="sys-whonix",
        destroy_after_stop=False,
    )

    assignment.validate()


def test_empty_persona_id_is_rejected() -> None:
    assignment = QubeAssignment(
        persona_id="",
        qube_name="spot-persona-01",
    )

    with pytest.raises(ValueError):
        assignment.validate()


def test_empty_qube_name_is_rejected() -> None:
    assignment = QubeAssignment(
        persona_id="alex",
        qube_name="",
    )

    with pytest.raises(ValueError):
        assignment.validate()


def test_disposable_qube_requires_destruction() -> None:
    assignment = QubeAssignment(
        persona_id="riley",
        qube_name="spot-disposable-01",
        qube_type=QubeType.DISPOSABLE,
        destroy_after_stop=False,
    )

    with pytest.raises(ValueError):
        assignment.validate()


def test_persistent_qube_cannot_be_destroy_after_stop() -> None:
    assignment = QubeAssignment(
        persona_id="alex",
        qube_name="spot-persona-01",
        qube_type=QubeType.APPVM,
        destroy_after_stop=True,
    )

    with pytest.raises(ValueError):
        assignment.validate()


def test_whonix_assignment_requires_network_qube() -> None:
    assignment = QubeAssignment(
        persona_id="alex",
        qube_name="spot-persona-01",
        network_mode=QubesNetworkMode.WHONIX,
        network_qube="",
    )

    with pytest.raises(ValueError):
        assignment.validate()


def test_offline_assignment_is_allowed() -> None:
    assignment = QubeAssignment(
        persona_id="alex",
        qube_name="spot-persona-01",
        network_mode=QubesNetworkMode.OFFLINE,
        network_qube="",
    )

    assignment.validate()

    assert assignment.network_mode == QubesNetworkMode.OFFLINE


def test_add_assignment() -> None:
    plugin = make_plugin()

    assignment = QubeAssignment(
        persona_id="alex",
        qube_name="spot-persona-01",
    )

    plugin.add_assignment(assignment)

    assert plugin.assignment_for("alex") == assignment


def test_duplicate_assignment_is_rejected() -> None:
    assignment = QubeAssignment(
        persona_id="alex",
        qube_name="spot-persona-01",
    )

    plugin = make_plugin(
        {"alex": assignment}
    )

    with pytest.raises(ValueError):
        plugin.add_assignment(assignment)


def test_remove_assignment() -> None:
    assignment = QubeAssignment(
        persona_id="alex",
        qube_name="spot-persona-01",
    )

    plugin = make_plugin(
        {"alex": assignment}
    )

    removed = plugin.remove_assignment("alex")

    assert removed == assignment

    with pytest.raises(KeyError):
        plugin.assignment_for("alex")


def test_validate_assignment() -> None:
    assignment = QubeAssignment(
        persona_id="alex",
        qube_name="spot-persona-01",
        network_mode=QubesNetworkMode.WHONIX,
        network_qube="sys-whonix",
    )

    plugin = make_plugin(
        {"alex": assignment}
    )

    assert plugin.validate_assignment("alex") is True


def test_non_whonix_network_is_rejected_when_required() -> None:
    assignment = QubeAssignment(
        persona_id="alex",
        qube_name="spot-persona-01",
        network_mode=QubesNetworkMode.OFFLINE,
        network_qube="",
    )

    plugin = make_plugin(
        {"alex": assignment}
    )

    # Offline is allowed as a non-networked state.
    assert plugin.validate_assignment("alex") is True


def test_whonix_network_is_allowed() -> None:
    assignment = QubeAssignment(
        persona_id="alex",
        qube_name="spot-persona-01",
        network_mode=QubesNetworkMode.WHONIX,
        network_qube="sys-whonix",
    )

    plugin = make_plugin(
        {"alex": assignment}
    )

    assert plugin.network_allowed("alex") is True


def test_offline_network_is_not_allowed_for_network_activity() -> None:
    assignment = QubeAssignment(
        persona_id="alex",
        qube_name="spot-persona-01",
        network_mode=QubesNetworkMode.OFFLINE,
        network_qube="",
    )

    plugin = make_plugin(
        {"alex": assignment}
    )

    assert plugin.network_allowed("alex") is False


def test_disabled_assignment_cannot_use_network() -> None:
    assignment = QubeAssignment(
        persona_id="alex",
        qube_name="spot-persona-01",
        enabled=False,
    )

    plugin = make_plugin(
        {"alex": assignment}
    )

    assert plugin.network_allowed("alex") is False


def test_emergency_stop_blocks_network() -> None:
    assignment = QubeAssignment(
        persona_id="alex",
        qube_name="spot-persona-01",
    )

    plugin = make_plugin(
        {"alex": assignment}
    )

    assert plugin.network_allowed("alex") is True

    assert plugin.emergency_stop() is True

    assert plugin.status == QubesPluginStatus.BLOCKED
    assert plugin.network_allowed("alex") is False


def test_emergency_stop_requires_explicit_reset() -> None:
    plugin = make_plugin()

    plugin.emergency_stop()

    assert plugin.start() is False

    assert plugin.reset_emergency_stop() is True
    assert plugin.start() is True


def test_rpc_policy_defaults_to_deny() -> None:
    policy = QubesRPCPolicy()

    assert policy.allows("spot-controller") is False
    assert policy.allows("unknown-service") is False


def test_explicit_rpc_service_can_be_allowed() -> None:
    policy = QubesRPCPolicy(
        allowed_services={"spot-controller"}
    )

    assert policy.allows("spot-controller") is True


def test_explicitly_denied_rpc_service_is_rejected() -> None:
    policy = QubesRPCPolicy(
        allowed_services={"admin.vm.Create"}
    )

    assert policy.allows("admin.vm.Create") is False


def test_qubes_detection_does_not_execute_management_commands(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    plugin = QubesPlugin()

    calls = []

    def fake_which(command):
        calls.append(command)
        return "/usr/bin/qvm-check"

    monkeypatch.setattr(
        shutil,
        "which",
        fake_which,
    )

    assert plugin.detect_qubes() is True
    assert calls == ["qvm-check"]


def test_summary_does_not_include_personal_data() -> None:
    plugin = make_plugin()

    summary = plugin.summary()

    assert "password" not in summary
    assert "credentials" not in summary
    assert "personal_data" not in summary


def test_no_arbitrary_dom0_interface() -> None:
    plugin = make_plugin()

    assert not hasattr(plugin, "execute_dom0")
    assert not hasattr(plugin, "execute_command")
    assert not hasattr(plugin, "shell")
    assert not hasattr(plugin, "run_qvm_command")
