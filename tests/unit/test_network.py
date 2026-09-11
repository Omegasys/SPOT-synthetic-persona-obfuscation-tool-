from spot.network.routing import NetworkMode, RoutingPolicy
from spot.network.dns import DNSPolicy, DNSRequest, DNSManager
from spot.network.firewall import FirewallPolicy, FirewallRule
from spot.network.kill_switch import KillSwitch


def test_network_mode_whonix():
    policy = RoutingPolicy(
        mode=NetworkMode.WHONIX,
        fail_closed=True,
        allow_fallback=False,
    )

    assert policy.mode == NetworkMode.WHONIX
    assert policy.fail_closed is True
    assert policy.allow_fallback is False


def test_private_destinations_are_blocked():
    policy = DNSPolicy(
        block_private=True,
    )

    manager = DNSManager(policy)

    request = DNSRequest(
        domain="localhost",
    )

    assert manager.validate(request) is False


def test_dns_allowlist():
    policy = DNSPolicy(
        allowlist_enabled=True,
        allowed_domains=["example.com"],
    )

    manager = DNSManager(policy)

    allowed = DNSRequest(domain="example.com")
    denied = DNSRequest(domain="not-example.com")

    assert manager.validate(allowed) is True
    assert manager.validate(denied) is False


def test_firewall_default_deny():
    policy = FirewallPolicy(
        default_allow=False,
    )

    assert policy.default_allow is False


def test_firewall_rule():
    rule = FirewallRule(
        action="allow",
        protocol="tcp",
        port=443,
    )

    assert rule.action == "allow"
    assert rule.protocol == "tcp"
    assert rule.port == 443


def test_kill_switch():
    kill_switch = KillSwitch()

    assert kill_switch.allows_network() is True

    kill_switch.enable()
    kill_switch.arm()
    kill_switch.activate()

    assert kill_switch.allows_network() is False

    kill_switch.deactivate()
    kill_switch.disable()

    assert kill_switch.allows_network() is True
