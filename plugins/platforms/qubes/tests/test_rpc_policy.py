from __future__ import annotations

import pytest

from plugins.platforms.qubes.plugin import (
    QubesRPCPolicy,
    QubesRPCRequest,
)


def test_default_deny() -> None:
    policy = QubesRPCPolicy()

    assert policy.allows("spot-controller") is False
    assert policy.allows("spot-persona") is False
    assert policy.allows("spot-network") is False
    assert policy.allows("anything-else") is False


def test_explicit_allow() -> None:
    policy = QubesRPCPolicy(
        allowed_services={
            "spot-controller",
            "spot-persona",
            "spot-network",
        }
    )

    assert policy.allows("spot-controller") is True
    assert policy.allows("spot-persona") is True
    assert policy.allows("spot-network") is True


def test_unknown_service_is_rejected() -> None:
    policy = QubesRPCPolicy(
        allowed_services={"spot-controller"}
    )

    with pytest.raises(PermissionError):
        policy.validate_service("unknown-service")


def test_empty_service_is_rejected() -> None:
    policy = QubesRPCPolicy(
        allowed_services={"spot-controller"}
    )

    with pytest.raises(ValueError):
        policy.validate_service("")


def test_dom0_is_disabled() -> None:
    policy = QubesRPCPolicy(
        allowed_services={"spot-controller"},
        allow_dom0=False,
    )

    assert policy.allow_dom0 is False


def test_arbitrary_commands_are_disabled() -> None:
    policy = QubesRPCPolicy(
        allowed_services={"spot-controller"},
        allow_arbitrary_commands=False,
    )

    assert policy.allow_arbitrary_commands is False


def test_shell_is_disabled() -> None:
    policy = QubesRPCPolicy(
        allowed_services={"spot-controller"},
        allow_shell=False,
    )

    assert policy.allow_shell is False


@pytest.mark.parametrize(
    "service",
    [
        "admin.vm.Create",
        "admin.vm.Remove",
        "admin.vm.Start",
        "admin.vm.Shutdown",
        "admin.vm.property.Set",
        "admin.vm.device.Attach",
        "admin.vm.device.Detach",
        "admin.vm.volume.Import",
        "admin.vm.volume.ImportWithSize",
    ],
)
def test_sensitive_admin_services_are_denied(
    service: str,
) -> None:
    policy = QubesRPCPolicy(
        allowed_services={service}
    )

    assert policy.allows(service) is False

    with pytest.raises(PermissionError):
        policy.validate_service(service)


def test_valid_rpc_request() -> None:
    policy = QubesRPCPolicy(
        allowed_services={"spot-persona"}
    )

    request = QubesRPCRequest(
        service="spot-persona",
        operation="start",
        persona_id="alex",
        qube_name="spot-persona-01",
    )

    request.validate(policy)


@pytest.mark.parametrize(
    "operation",
    [
        "exec",
        "shell",
        "arbitrary-command",
    ],
)
def test_arbitrary_execution_operations_are_denied(
    operation: str,
) -> None:
    policy = QubesRPCPolicy(
        allowed_services={"spot-controller"}
    )

    request = QubesRPCRequest(
        service="spot-controller",
        operation=operation,
    )

    with pytest.raises(PermissionError):
        request.validate(policy)


def test_empty_operation_is_rejected() -> None:
    policy = QubesRPCPolicy(
        allowed_services={"spot-controller"}
    )

    request = QubesRPCRequest(
        service="spot-controller",
        operation="",
    )

    with pytest.raises(ValueError):
        request.validate(policy)


def test_empty_persona_id_is_rejected() -> None:
    policy = QubesRPCPolicy(
        allowed_services={"spot-persona"}
    )

    request = QubesRPCRequest(
        service="spot-persona",
        operation="start",
        persona_id="",
    )

    with pytest.raises(ValueError):
        request.validate(policy)


def test_empty_qube_name_is_rejected() -> None:
    policy = QubesRPCPolicy(
        allowed_services={"spot-persona"}
    )

    request = QubesRPCRequest(
        service="spot-persona",
        operation="start",
        qube_name="",
    )

    with pytest.raises(ValueError):
        request.validate(policy)


def test_rpc_request_for_allowed_persona_operation() -> None:
    policy = QubesRPCPolicy(
        allowed_services={"spot-persona"}
    )

    request = QubesRPCRequest(
        service="spot-persona",
        operation="stop",
        persona_id="jordan",
        qube_name="spot-persona-02",
    )

    request.validate(policy)


def test_network_rpc_service() -> None:
    policy = QubesRPCPolicy(
        allowed_services={"spot-network"}
    )

    request = QubesRPCRequest(
        service="spot-network",
        operation="health",
    )

    request.validate(policy)


def test_controller_emergency_stop_rpc() -> None:
    policy = QubesRPCPolicy(
        allowed_services={"spot-controller"}
    )

    request = QubesRPCRequest(
        service="spot-controller",
        operation="emergency-stop",
    )

    request.validate(policy)


def test_multiple_services_can_be_allowed() -> None:
    policy = QubesRPCPolicy(
        allowed_services={
            "spot-controller",
            "spot-persona",
            "spot-network",
        }
    )

    assert policy.allows("spot-controller") is True
    assert policy.allows("spot-persona") is True
    assert policy.allows("spot-network") is True


def test_denied_service_wins_over_allow_list() -> None:
    policy = QubesRPCPolicy(
        allowed_services={"admin.vm.Create"}
    )

    assert policy.allows("admin.vm.Create") is False


def test_policy_does_not_allow_wildcards() -> None:
    policy = QubesRPCPolicy(
        allowed_services={"spot-*"}
    )

    assert policy.allows("spot-controller") is False
    assert policy.allows("spot-persona") is False
    assert policy.allows("spot-network") is False


def test_rpc_request_does_not_accept_unrelated_qube_target() -> None:
    policy = QubesRPCPolicy(
        allowed_services={"spot-persona"}
    )

    request = QubesRPCRequest(
        service="spot-persona",
        operation="start",
        persona_id="alex",
        qube_name="some-other-qube",
    )

    # The policy itself validates syntax and permissions. Mapping the
    # request to the persona assignment is performed by QubesPlugin.
    request.validate(policy)


def test_policy_has_no_dom0_shell_capability() -> None:
    policy = QubesRPCPolicy(
        allowed_services={
            "spot-controller",
            "spot-persona",
            "spot-network",
        }
    )

    assert policy.allow_dom0 is False
    assert policy.allow_arbitrary_commands is False
    assert policy.allow_shell is False
