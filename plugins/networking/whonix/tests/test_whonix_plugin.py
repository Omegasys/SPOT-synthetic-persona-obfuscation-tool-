from __future__ import annotations

import socket

import pytest

from plugins.networking.whonix.plugin import (
    WhonixConfig,
    WhonixHealth,
    WhonixPlugin,
    WhonixStatus,
    WhonixTopology,
)


class DummyContext:
    """Minimal plugin context used by offline tests."""


def make_plugin(
    config: WhonixConfig | None = None,
) -> WhonixPlugin:
    """Create an initialized and started test plugin."""

    plugin = WhonixPlugin(config)
    assert plugin.initialize(DummyContext()) is True
    assert plugin.start() is True

    return plugin


def test_metadata() -> None:
    assert WhonixPlugin.metadata.id == "network-whonix"
    assert WhonixPlugin.metadata.name == "Whonix Networking Plugin"
    assert WhonixPlugin.metadata.version == "0.1.0"


def test_default_configuration_is_fail_closed() -> None:
    config = WhonixConfig()

    assert config.fail_closed is True
    assert config.allow_direct_fallback is False
    assert config.require_gateway is True
    assert config.require_tor is True
    assert config.prevent_dns_bypass is True


def test_default_topology_is_qubes() -> None:
    config = WhonixConfig()

    assert config.topology == WhonixTopology.QUBES


def test_plugin_lifecycle() -> None:
    plugin = WhonixPlugin()

    assert plugin.status == WhonixStatus.DISABLED
    assert plugin.initialize(DummyContext()) is True
    assert plugin.status == WhonixStatus.CONFIGURED

    assert plugin.start() is True
    assert plugin.health_check() is True

    assert plugin.stop() is True
    assert plugin.health_check() is False


def test_disabled_plugin_cannot_start() -> None:
    config = WhonixConfig(enabled=False)
    plugin = WhonixPlugin(config)

    assert plugin.initialize(DummyContext()) is True
    assert plugin.status == WhonixStatus.DISABLED

    assert plugin.start() is False
    assert plugin.health_check() is False


def test_uninitialized_plugin_cannot_create_route() -> None:
    plugin = WhonixPlugin()

    with pytest.raises(RuntimeError):
        plugin.route()


def test_disabled_plugin_cannot_create_route() -> None:
    plugin = WhonixPlugin(
        WhonixConfig(enabled=False)
    )

    assert plugin.initialize(DummyContext()) is True

    with pytest.raises(RuntimeError):
        plugin.route()


def test_route_contains_expected_configuration() -> None:
    plugin = make_plugin()

    route = plugin.route()

    assert route.topology == WhonixTopology.QUBES
    assert route.gateway_host == "sys-whonix"
    assert route.gateway_port == 9050
    assert route.workstation_name == "anon-whonix"
    assert route.require_gateway is True
    assert route.require_tor is True
    assert route.fail_closed is True
    assert route.prevent_dns_bypass is True


def test_gateway_endpoint() -> None:
    plugin = make_plugin()

    assert plugin.gateway_endpoint() == "sys-whonix:9050"


def test_invalid_gateway_port() -> None:
    config = WhonixConfig(gateway_port=0)

    with pytest.raises(ValueError):
        config.validate()


def test_invalid_gateway_port_too_high() -> None:
    config = WhonixConfig(gateway_port=65536)

    with pytest.raises(ValueError):
        config.validate()


def test_invalid_timeout() -> None:
    config = WhonixConfig(connect_timeout=0)

    with pytest.raises(ValueError):
        config.validate()


def test_empty_gateway_is_rejected() -> None:
    config = WhonixConfig(gateway_host="")

    with pytest.raises(ValueError):
        config.validate()


def test_empty_workstation_is_rejected() -> None:
    config = WhonixConfig(workstation_name="")

    with pytest.raises(ValueError):
        config.validate()


def test_fail_closed_disallows_direct_fallback() -> None:
    config = WhonixConfig(
        fail_closed=True,
        allow_direct_fallback=True,
    )

    with pytest.raises(ValueError):
        config.validate()


def test_direct_fallback_is_disabled_by_default() -> None:
    plugin = make_plugin()

    assert plugin.can_fallback_direct() is False


def test_direct_fallback_requires_explicit_non_fail_closed_policy() -> None:
    config = WhonixConfig(
        fail_closed=False,
        allow_direct_fallback=True,
    )

    plugin = make_plugin(config)

    assert plugin.can_fallback_direct() is True


def test_network_is_not_allowed_before_start() -> None:
    plugin = WhonixPlugin()

    assert plugin.initialize(DummyContext()) is True
    assert plugin.network_allowed() is False

    assert plugin.start() is True
    assert plugin.network_allowed() is True


def test_network_is_not_allowed_when_disabled() -> None:
    config = WhonixConfig(enabled=False)
    plugin = WhonixPlugin(config)

    assert plugin.initialize(DummyContext()) is True
    assert plugin.network_allowed() is False


def test_health_check_without_running_plugin() -> None:
    plugin = WhonixPlugin()

    assert plugin.initialize(DummyContext()) is True

    health = plugin.check_gateway()

    assert isinstance(health, WhonixHealth)
    assert health.status == WhonixStatus.UNAVAILABLE
    assert "not running" in health.message


def test_health_check_disabled_plugin() -> None:
    config = WhonixConfig(enabled=False)
    plugin = WhonixPlugin(config)

    assert plugin.initialize(DummyContext()) is True

    health = plugin.check_gateway()

    assert health.status == WhonixStatus.DISABLED


def test_health_check_with_mocked_gateway(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    plugin = make_plugin(
        WhonixConfig(
            gateway_host="example.test",
            gateway_port=9050,
        )
    )

    class DummySocket:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_create_connection(address, timeout):
        assert address == ("example.test", 9050)
        assert timeout == 5.0
        return DummySocket()

    monkeypatch.setattr(
        socket,
        "create_connection",
        fake_create_connection,
    )

    health = plugin.check_gateway()

    assert health.status == WhonixStatus.AVAILABLE
    assert health.latency_ms is not None
    assert health.message == "Whonix Gateway endpoint is reachable."


def test_health_check_unavailable_gateway(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    plugin = make_plugin()

    def fake_create_connection(address, timeout):
        raise OSError("connection refused")

    monkeypatch.setattr(
        socket,
        "create_connection",
        fake_create_connection,
    )

    health = plugin.check_gateway()

    assert health.status == WhonixStatus.UNAVAILABLE
    assert "connection refused" in health.message


def test_health_check_does_not_require_internet(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    plugin = make_plugin()

    calls = []

    class DummySocket:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_create_connection(address, timeout):
        calls.append((address, timeout))
        return DummySocket()

    monkeypatch.setattr(
        socket,
        "create_connection",
        fake_create_connection,
    )

    health = plugin.check_gateway()

    assert health.status == WhonixStatus.AVAILABLE
    assert len(calls) == 1
    assert calls[0][0] == ("sys-whonix", 9050)


def test_topology_summary() -> None:
    plugin = make_plugin()

    summary = plugin.topology_summary()

    assert summary["topology"] == "qubes"
    assert summary["gateway_host"] == "sys-whonix"
    assert summary["gateway_port"] == 9050
    assert summary["workstation_name"] == "anon-whonix"
    assert summary["fail_closed"] is True
    assert summary["direct_fallback_allowed"] is False
    assert summary["prevent_dns_bypass"] is True


def test_fail_closed_property() -> None:
    plugin = make_plugin()

    assert plugin.is_fail_closed() is True


def test_emergency_stop_blocks_plugin() -> None:
    plugin = make_plugin()

    assert plugin.network_allowed() is True

    assert plugin.emergency_stop() is True

    assert plugin.status == WhonixStatus.BLOCKED
    assert plugin.network_allowed() is False


def test_emergency_stop_does_not_modify_host_networking() -> None:
    plugin = make_plugin()

    assert plugin.emergency_stop() is True

    # The plugin only changes its own policy state.
    # Actual network shutdown belongs to the platform backend.
    assert plugin.status == WhonixStatus.BLOCKED


def test_generic_topology_is_supported() -> None:
    config = WhonixConfig(
        topology=WhonixTopology.GENERIC,
        gateway_host="127.0.0.1",
        gateway_port=9050,
    )

    plugin = make_plugin(config)

    route = plugin.route()

    assert route.topology == WhonixTopology.GENERIC


def test_custom_gateway_configuration() -> None:
    config = WhonixConfig(
        gateway_host="10.0.0.2",
        gateway_port=9150,
        workstation_name="spot-whonix",
    )

    plugin = make_plugin(config)

    assert plugin.gateway_endpoint() == "10.0.0.2:9150"

    route = plugin.route()

    assert route.workstation_name == "spot-whonix"


def test_timeout_argument_must_be_positive() -> None:
    plugin = make_plugin()

    with pytest.raises(ValueError):
        plugin.check_gateway(timeout=0)


def test_no_privileged_operations_are_exposed() -> None:
    plugin = make_plugin()

    assert not hasattr(plugin, "modify_firewall")
    assert not hasattr(plugin, "modify_routes")
    assert not hasattr(plugin, "manage_dom0")
    assert not hasattr(plugin, "execute_privileged")


def test_qubes_configuration_is_explicit() -> None:
    config = WhonixConfig(
        topology=WhonixTopology.QUBES,
        gateway_host="sys-whonix",
        workstation_name="anon-whonix",
    )

    config.validate()

    assert config.topology == WhonixTopology.QUBES
