from spot.network.manager import NetworkManager
from spot.network.routing import NetworkMode, RoutingPolicy
from spot.network.dns import DNSManager, DNSPolicy, DNSRequest


def test_whonix_mode_is_fail_closed():
    policy = RoutingPolicy(
        mode=NetworkMode.WHONIX,
        fail_closed=True,
        allow_fallback=False,
    )

    manager = NetworkManager(routing_policy=policy)

    assert manager.active_mode() == NetworkMode.WHONIX
    assert policy.fail_closed is True
    assert policy.allow_fallback is False


def test_network_does_not_fallback_to_direct():
    policy = RoutingPolicy(
        mode=NetworkMode.WHONIX,
        fail_closed=True,
        allow_fallback=False,
    )

    manager = NetworkManager(routing_policy=policy)

    assert manager.routing_policy.allow_fallback is False


def test_dns_policy_blocks_private_destinations():
    policy = DNSPolicy(
        block_private=True,
    )

    dns = DNSManager(policy)

    private_requests = [
        DNSRequest(domain="localhost"),
        DNSRequest(domain="127.0.0.1"),
    ]

    for request in private_requests:
        assert dns.validate(request) is False


def test_dns_allowlist_prevents_unapproved_destinations():
    policy = DNSPolicy(
        allowlist_enabled=True,
        allowed_domains=["example.com"],
    )

    dns = DNSManager(policy)

    assert dns.validate(
        DNSRequest(domain="example.com")
    ) is True

    assert dns.validate(
        DNSRequest(domain="not-approved.example")
    ) is False


def test_network_health_failure_does_not_enable_direct_fallback():
    policy = RoutingPolicy(
        mode=NetworkMode.WHONIX,
        fail_closed=True,
        allow_fallback=False,
    )

    manager = NetworkManager(routing_policy=policy)

    manager.stop()

    assert manager.can_connect() is False
    assert manager.routing_policy.allow_fallback is False
