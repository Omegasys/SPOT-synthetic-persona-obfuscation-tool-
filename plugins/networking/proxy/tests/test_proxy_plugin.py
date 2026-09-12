from __future__ import annotations

import socket

import pytest

from plugins.networking.proxy.plugin import (
    ProxyConfig,
    ProxyHealth,
    ProxyPlugin,
    ProxyStatus,
    ProxyType,
)


class DummyContext:
    """Minimal plugin context used by offline tests."""


def make_plugin(
    config: ProxyConfig | None = None,
) -> ProxyPlugin:
    """Create an initialized and started test plugin."""

    plugin = ProxyPlugin(config)

    assert plugin.initialize(DummyContext()) is True
    assert plugin.start() is True

    return plugin


@pytest.mark.parametrize(
    "proxy_type",
    [
        ProxyType.HTTP,
        ProxyType.HTTPS,
        ProxyType.SOCKS5,
        ProxyType.SOCKS5H,
    ],
)
def test_supported_proxy_types(proxy_type: ProxyType) -> None:
    config = ProxyConfig(proxy_type=proxy_type)

    config.validate()

    assert config.proxy_type == proxy_type


def test_metadata() -> None:
    assert ProxyPlugin.metadata.id == "network-proxy"
    assert ProxyPlugin.metadata.name == "Proxy Networking Plugin"
    assert ProxyPlugin.metadata.version == "0.1.0"


def test_default_configuration_is_fail_closed() -> None:
    config = ProxyConfig()

    assert config.fail_closed is True
    assert config.allow_direct_fallback is False
    assert config.authentication_enabled is False
    assert config.allow_proxy_chaining is False


def test_plugin_lifecycle() -> None:
    plugin = ProxyPlugin()

    assert plugin.status == ProxyStatus.DISABLED

    assert plugin.initialize(DummyContext()) is True
    assert plugin.status == ProxyStatus.CONFIGURED

    assert plugin.start() is True
    assert plugin.health_check() is True

    assert plugin.stop() is True
    assert plugin.health_check() is False


def test_disabled_plugin_cannot_start() -> None:
    plugin = ProxyPlugin(
        ProxyConfig(enabled=False)
    )

    assert plugin.initialize(DummyContext()) is True
    assert plugin.status == ProxyStatus.DISABLED

    assert plugin.start() is False
    assert plugin.health_check() is False


def test_uninitialized_plugin_cannot_create_route() -> None:
    plugin = ProxyPlugin()

    with pytest.raises(RuntimeError):
        plugin.route()


def test_disabled_plugin_cannot_create_route() -> None:
    plugin = ProxyPlugin(
        ProxyConfig(enabled=False)
    )

    assert plugin.initialize(DummyContext()) is True

    with pytest.raises(RuntimeError):
        plugin.route()


def test_route_contains_expected_configuration() -> None:
    plugin = make_plugin(
        ProxyConfig(
            proxy_type=ProxyType.SOCKS5,
            host="127.0.0.1",
            port=9050,
        )
    )

    route = plugin.route()

    assert route.proxy_type == ProxyType.SOCKS5
    assert route.host == "127.0.0.1"
    assert route.port == 9050
    assert route.fail_closed is True
    assert route.strict is True


def test_proxy_url_without_credentials() -> None:
    plugin = make_plugin(
        ProxyConfig(
            proxy_type=ProxyType.SOCKS5,
            host="127.0.0.1",
            port=9050,
        )
    )

    assert plugin.proxy_url() == "socks5://127.0.0.1:9050"


@pytest.mark.parametrize(
    "proxy_type,expected",
    [
        (ProxyType.HTTP, "http://127.0.0.1:8080"),
        (ProxyType.HTTPS, "https://127.0.0.1:8443"),
        (ProxyType.SOCKS5, "socks5://127.0.0.1:9050"),
        (ProxyType.SOCKS5H, "socks5h://127.0.0.1:9050"),
    ],
)
def test_proxy_url_formats(
    proxy_type: ProxyType,
    expected: str,
) -> None:
    plugin = make_plugin(
        ProxyConfig(
            proxy_type=proxy_type,
            port=int(expected.rsplit(":", 1)[1]),
        )
    )

    assert plugin.proxy_url() == expected


def test_empty_host_is_rejected() -> None:
    config = ProxyConfig(host="")

    with pytest.raises(ValueError):
        config.validate()


def test_invalid_port_zero_is_rejected() -> None:
    config = ProxyConfig(port=0)

    with pytest.raises(ValueError):
        config.validate()


def test_invalid_port_too_high_is_rejected() -> None:
    config = ProxyConfig(port=65536)

    with pytest.raises(ValueError):
        config.validate()


def test_invalid_timeout_is_rejected() -> None:
    config = ProxyConfig(connect_timeout=0)

    with pytest.raises(ValueError):
        config.validate()


def test_fail_closed_disallows_direct_fallback() -> None:
    config = ProxyConfig(
        fail_closed=True,
        allow_direct_fallback=True,
    )

    with pytest.raises(ValueError):
        config.validate()


def test_direct_fallback_is_disabled_by_default() -> None:
    plugin = make_plugin()

    assert plugin.can_fallback_direct() is False


def test_direct_fallback_requires_explicit_policy() -> None:
    config = ProxyConfig(
        fail_closed=False,
        allow_direct_fallback=True,
    )

    plugin = make_plugin(config)

    assert plugin.can_fallback_direct() is True


def test_authentication_is_disabled_by_default() -> None:
    config = ProxyConfig()

    config.validate()

    assert config.authentication_enabled is False
    assert config.username is None
    assert config.password is None


def test_username_without_authentication_is_rejected() -> None:
    config = ProxyConfig(
        authentication_enabled=False,
        username="example",
    )

    with pytest.raises(ValueError):
        config.validate()


def test_password_without_authentication_is_rejected() -> None:
    config = ProxyConfig(
        authentication_enabled=False,
        password="secret",
    )

    with pytest.raises(ValueError):
        config.validate()


def test_missing_username_with_authentication_is_rejected() -> None:
    config = ProxyConfig(
        authentication_enabled=True,
        password="secret",
    )

    with pytest.raises(ValueError):
        config.validate()


def test_missing_password_with_authentication_is_rejected() -> None:
    config = ProxyConfig(
        authentication_enabled=True,
        username="example",
    )

    with pytest.raises(ValueError):
        config.validate()


def test_authenticated_route_does_not_expose_credentials_by_default() -> None:
    config = ProxyConfig(
        authentication_enabled=True,
        username="example-user",
        password="secret",
    )

    plugin = make_plugin(config)

    route = plugin.route()

    assert route.as_url() == "socks5://127.0.0.1:8080"
    assert "secret" not in route.as_url()
    assert "example-user" not in route.as_url()


def test_authenticated_route_can_include_username_only() -> None:
    config = ProxyConfig(
        authentication_enabled=True,
        username="example-user",
        password="secret",
    )

    plugin = make_plugin(config)

    route = plugin.route()

    assert (
        route.as_url(include_credentials=True)
        == "socks5://example-user@127.0.0.1:8080"
    )

    assert "secret" not in route.as_url(
        include_credentials=True
    )


def test_proxy_chaining_is_rejected() -> None:
    config = ProxyConfig(
        allow_proxy_chaining=True,
    )

    with pytest.raises(ValueError):
        config.validate()


def test_network_is_not_allowed_before_start() -> None:
    plugin = ProxyPlugin()

    assert plugin.initialize(DummyContext()) is True
    assert plugin.network_allowed() is False

    assert plugin.start() is True
    assert plugin.network_allowed() is True


def test_network_is_not_allowed_when_disabled() -> None:
    plugin = ProxyPlugin(
        ProxyConfig(enabled=False)
    )

    assert plugin.initialize(DummyContext()) is True
    assert plugin.network_allowed() is False


def test_health_check_without_running_plugin() -> None:
    plugin = ProxyPlugin()

    assert plugin.initialize(DummyContext()) is True

    health = plugin.check_endpoint()

    assert isinstance(health, ProxyHealth)
    assert health.status == ProxyStatus.UNAVAILABLE
    assert "not running" in health.message


def test_health_check_disabled_plugin() -> None:
    plugin = ProxyPlugin(
        ProxyConfig(enabled=False)
    )

    assert plugin.initialize(DummyContext()) is True

    health = plugin.check_endpoint()

    assert health.status == ProxyStatus.DISABLED


def test_health_check_with_mocked_endpoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    plugin = make_plugin(
        ProxyConfig(
            proxy_type=ProxyType.SOCKS5,
            host="proxy.example",
            port=9050,
        )
    )

    class DummySocket:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_create_connection(address, timeout):
        assert address == ("proxy.example", 9050)
        assert timeout == 5.0

        return DummySocket()

    monkeypatch.setattr(
        socket,
        "create_connection",
        fake_create_connection,
    )

    health = plugin.check_endpoint()

    assert health.status == ProxyStatus.AVAILABLE
    assert health.latency_ms is not None
    assert health.message == "Proxy endpoint is reachable."


def test_health_check_unavailable_endpoint(
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

    health = plugin.check_endpoint()

    assert health.status == ProxyStatus.UNAVAILABLE
    assert "connection refused" in health.message


def test_health_check_does_not_make_internet_request(
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

    health = plugin.check_endpoint()

    assert health.status == ProxyStatus.AVAILABLE
    assert len(calls) == 1
    assert calls[0][0] == ("127.0.0.1", 8080)


def test_custom_timeout_is_used(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    plugin = make_plugin()

    observed = {}

    class DummySocket:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_create_connection(address, timeout):
        observed["address"] = address
        observed["timeout"] = timeout

        return DummySocket()

    monkeypatch.setattr(
        socket,
        "create_connection",
        fake_create_connection,
    )

    health = plugin.check_endpoint(timeout=2.5)

    assert health.status == ProxyStatus.AVAILABLE
    assert observed["timeout"] == 2.5


def test_invalid_health_timeout_is_rejected() -> None:
    plugin = make_plugin()

    with pytest.raises(ValueError):
        plugin.check_endpoint(timeout=0)


def test_routing_summary_does_not_include_password() -> None:
    config = ProxyConfig(
        authentication_enabled=True,
        username="example-user",
        password="super-secret",
    )

    plugin = make_plugin(config)

    summary = plugin.routing_summary()

    assert summary["authentication_enabled"] is True
    assert "password" not in summary
    assert "super-secret" not in str(summary)


def test_emergency_stop_blocks_plugin() -> None:
    plugin = make_plugin()

    assert plugin.network_allowed() is True

    assert plugin.emergency_stop() is True

    assert plugin.status == ProxyStatus.BLOCKED
    assert plugin.network_allowed() is False


def test_emergency_stop_does_not_modify_host_networking() -> None:
    plugin = make_plugin()

    assert plugin.emergency_stop() is True

    # The plugin only changes its own state.
    # Actual network shutdown belongs to the platform backend.
    assert plugin.status == ProxyStatus.BLOCKED


def test_supported_protocol_values() -> None:
    assert ProxyType.HTTP.value == "http"
    assert ProxyType.HTTPS.value == "https"
    assert ProxyType.SOCKS5.value == "socks5"
    assert ProxyType.SOCKS5H.value == "socks5h"


def test_no_privileged_operations_are_exposed() -> None:
    plugin = make_plugin()

    assert not hasattr(plugin, "modify_firewall")
    assert not hasattr(plugin, "modify_routes")
    assert not hasattr(plugin, "execute_privileged")
    assert not hasattr(plugin, "manage_dom0")


def test_plugin_does_not_allow_proxy_chaining() -> None:
    plugin = make_plugin()

    assert plugin.config.allow_proxy_chaining is False
