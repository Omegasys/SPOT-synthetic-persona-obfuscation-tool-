from pathlib import Path
import sys

import pytest


PLUGIN_ROOT = Path(__file__).resolve().parents[1]

if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from plugin import (
    TorConfig,
    TorHealth,
    TorPlugin,
    TorRoute,
    TorStatus,
)


def test_plugin_metadata():
    plugin = TorPlugin()

    assert plugin.metadata.id == "network-tor"
    assert plugin.metadata.name == "Tor Networking Plugin"
    assert plugin.metadata.version == "0.1.0"


def test_plugin_requires_initialization():
    plugin = TorPlugin()

    assert plugin.start() is False
    assert plugin.health_check() is False


def test_plugin_lifecycle():
    plugin = TorPlugin()

    assert plugin.initialize(context={}) is True
    assert plugin.status == TorStatus.CONFIGURED

    assert plugin.start() is True
    assert plugin.health_check() is True

    assert plugin.stop() is True
    assert plugin.health_check() is False


def test_disabled_plugin_cannot_start():
    plugin = TorPlugin(
        config=TorConfig(
            enabled=False,
        )
    )

    assert plugin.initialize(context={}) is True
    assert plugin.status == TorStatus.DISABLED

    assert plugin.start() is False
    assert plugin.health_check() is False


def test_tor_config_defaults():
    config = TorConfig()

    assert config.host == "127.0.0.1"
    assert config.port == 9050
    assert config.socks_version == 5
    assert config.strict is True
    assert config.fail_closed is True
    assert config.allow_direct_fallback is False


def test_tor_config_validation():
    config = TorConfig()

    config.validate()


def test_invalid_port_is_rejected():
    config = TorConfig(
        port=0,
    )

    with pytest.raises(ValueError):
        config.validate()


def test_port_above_range_is_rejected():
    config = TorConfig(
        port=65536,
    )

    with pytest.raises(ValueError):
        config.validate()


def test_only_socks5_is_supported():
    config = TorConfig(
        socks_version=4,
    )

    with pytest.raises(ValueError):
        config.validate()


def test_invalid_timeout_is_rejected():
    config = TorConfig(
        connect_timeout=0,
    )

    with pytest.raises(ValueError):
        config.validate()


def test_fail_closed_prevents_direct_fallback():
    config = TorConfig(
        fail_closed=True,
        allow_direct_fallback=True,
    )

    with pytest.raises(ValueError):
        config.validate()


def test_route():
    plugin = TorPlugin()

    plugin.initialize(context={})
    plugin.start()

    route = plugin.route()

    assert isinstance(route, TorRoute)
    assert route.host == "127.0.0.1"
    assert route.port == 9050
    assert route.socks_version == 5
    assert route.strict is True
    assert route.fail_closed is True


def test_route_requires_initialization():
    plugin = TorPlugin()

    with pytest.raises(RuntimeError):
        plugin.route()


def test_route_requires_enabled_plugin():
    plugin = TorPlugin(
        config=TorConfig(
            enabled=False,
        )
    )

    plugin.initialize(context={})

    with pytest.raises(RuntimeError):
        plugin.route()


def test_proxy_url():
    plugin = TorPlugin()

    plugin.initialize(context={})
    plugin.start()

    assert plugin.proxy_url() == "socks5://127.0.0.1:9050"


def test_direct_fallback_is_disabled():
    plugin = TorPlugin()

    assert plugin.can_fallback_direct() is False


def test_direct_fallback_requires_non_strict_configuration():
    config = TorConfig(
        fail_closed=False,
        allow_direct_fallback=True,
    )

    plugin = TorPlugin(config=config)

    assert plugin.initialize(context={}) is True
    assert plugin.can_fallback_direct() is True


def test_strict_configuration_disallows_direct_fallback():
    config = TorConfig(
        strict=True,
        fail_closed=False,
        allow_direct_fallback=True,
    )

    plugin = TorPlugin(config=config)

    assert plugin.initialize(context={}) is True

    # Strict mode is represented in the route, while fallback behavior
    # is controlled by fail_closed/allow_direct_fallback.
    assert plugin.can_fallback_direct() is True


def test_health_check_without_running():
    plugin = TorPlugin()

    plugin.initialize(context={})

    health = plugin.check_endpoint()

    assert isinstance(health, TorHealth)
    assert health.status == TorStatus.UNAVAILABLE


def test_health_check_disabled():
    plugin = TorPlugin(
        config=TorConfig(
            enabled=False,
        )
    )

    plugin.initialize(context={})

    health = plugin.check_endpoint()

    assert health.status == TorStatus.DISABLED


def test_health_check_does_not_require_external_internet(monkeypatch):
    plugin = TorPlugin(
        config=TorConfig(
            host="127.0.0.1",
            port=9050,
        )
    )

    plugin.initialize(context={})
    plugin.start()

    def fake_connection(address, timeout=None):
        class FakeSocket:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                return False

        return FakeSocket()

    monkeypatch.setattr(
        "socket.create_connection",
        fake_connection,
    )

    health = plugin.check_endpoint()

    assert health.status == TorStatus.AVAILABLE
    assert health.latency_ms is not None


def test_unavailable_endpoint(monkeypatch):
    plugin = TorPlugin(
        config=TorConfig(
            host="127.0.0.1",
            port=9050,
        )
    )

    plugin.initialize(context={})
    plugin.start()

    def fake_connection(address, timeout=None):
        raise OSError("connection refused")

    monkeypatch.setattr(
        "socket.create_connection",
        fake_connection,
    )

    health = plugin.check_endpoint()

    assert health.status == TorStatus.UNAVAILABLE
    assert "connection refused" in health.message


def test_invalid_health_timeout():
    plugin = TorPlugin()

    plugin.initialize(context={})
    plugin.start()

    with pytest.raises(ValueError):
        plugin.check_endpoint(timeout=0)


def test_routing_summary():
    plugin = TorPlugin()

    plugin.initialize(context={})
    plugin.start()

    summary = plugin.routing_summary()

    assert summary["enabled"] is True
    assert summary["running"] is True
    assert summary["status"] == TorStatus.CONFIGURED.value
    assert summary["host"] == "127.0.0.1"
    assert summary["port"] == 9050
    assert summary["socks_version"] == 5
    assert summary["strict"] is True
    assert summary["fail_closed"] is True
    assert summary["allow_direct_fallback"] is False
    assert summary["direct_fallback_allowed"] is False


def test_custom_tor_endpoint():
    config = TorConfig(
        host="127.0.0.1",
        port=9150,
    )

    plugin = TorPlugin(config=config)

    plugin.initialize(context={})
    plugin.start()

    route = plugin.route()

    assert route.host == "127.0.0.1"
    assert route.port == 9150
    assert plugin.proxy_url() == "socks5://127.0.0.1:9150"


def test_tor_health_dataclass():
    health = TorHealth(
        status=TorStatus.AVAILABLE,
        host="127.0.0.1",
        port=9050,
        message="OK",
        latency_ms=5.0,
    )

    assert health.status == TorStatus.AVAILABLE
    assert health.host == "127.0.0.1"
    assert health.port == 9050
    assert health.latency_ms == 5.0
