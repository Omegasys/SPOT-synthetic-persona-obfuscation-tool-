from spot.qubes.networking import (
    QubesNetworkMode,
    QubesNetworkPolicy,
    QubesNetworkManager,
    QubeNetworkAssignment,
)


def test_whonix_is_supported_network_mode():
    assert QubesNetworkMode.WHONIX is not None


def test_whonix_network_policy_is_fail_closed():
    policy = QubesNetworkPolicy(
        mode=QubesNetworkMode.WHONIX,
        fail_closed=True,
    )

    assert policy.mode == QubesNetworkMode.WHONIX
    assert policy.fail_closed is True


def test_direct_network_is_not_default():
    policy = QubesNetworkPolicy()

    assert policy.mode != QubesNetworkMode.DIRECT


def test_persona_network_assignment():
    manager = QubesNetworkManager()

    assignment = QubeNetworkAssignment(
        qube_name="spot-persona-a",
        mode=QubesNetworkMode.WHONIX,
        gateway="sys-whonix",
    )

    manager.assign(assignment)

    result = manager.get("spot-persona-a")

    assert result is assignment
    assert result.mode == QubesNetworkMode.WHONIX
    assert result.gateway == "sys-whonix"


def test_network_assignments_are_separate():
    manager = QubesNetworkManager()

    first = QubeNetworkAssignment(
        qube_name="spot-persona-a",
        mode=QubesNetworkMode.WHONIX,
        gateway="sys-whonix",
    )

    second = QubeNetworkAssignment(
        qube_name="spot-persona-b",
        mode=QubesNetworkMode.WHONIX,
        gateway="sys-whonix",
    )

    manager.assign(first)
    manager.assign(second)

    assert manager.get("spot-persona-a") is first
    assert manager.get("spot-persona-b") is second


def test_emergency_stop_disables_network_activity():
    manager = QubesNetworkManager()

    assignment = QubeNetworkAssignment(
        qube_name="spot-persona-a",
        mode=QubesNetworkMode.WHONIX,
        gateway="sys-whonix",
    )

    manager.assign(assignment)

    manager.emergency_stop()

    assert manager.active() == []


def test_network_reset_restores_configuration():
    manager = QubesNetworkManager()

    assignment = QubeNetworkAssignment(
        qube_name="spot-persona-a",
        mode=QubesNetworkMode.WHONIX,
        gateway="sys-whonix",
    )

    manager.assign(assignment)

    manager.emergency_stop()
    manager.reset()

    result = manager.get("spot-persona-a")

    assert result is assignment
