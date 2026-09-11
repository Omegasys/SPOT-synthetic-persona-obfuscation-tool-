from spot.safety.manager import SafetyManager
from spot.safety.limits import SafetyLimits
from spot.safety.allowlist import Allowlist
from spot.safety.blocklist import Blocklist
from spot.safety.rate_limit import RateLimiter
from spot.safety.bandwidth import BandwidthManager, BandwidthLimit
from spot.safety.resource_limits import (
    ResourceLimits,
    ResourceLimitManager,
)
from spot.safety.emergency_stop import EmergencyStop


def test_safety_manager_allows_safe_action():
    manager = SafetyManager()

    decision = manager.check(
        action="search",
        target="example.com",
    )

    assert decision.allowed is True


def test_safety_manager_blocks_dangerous_action():
    manager = SafetyManager()

    decision = manager.check(
        action="credential_theft",
        target="example.com",
    )

    assert decision.allowed is False


def test_blocklist():
    blocklist = Blocklist()

    assert blocklist.is_blocked("dos") is True
    assert blocklist.is_blocked("search") is False


def test_allowlist():
    allowlist = Allowlist(
        enabled=True,
        domains=["example.com"],
    )

    assert allowlist.is_allowed("example.com") is True
    assert allowlist.is_allowed("other.com") is False


def test_rate_limiter():
    limiter = RateLimiter(
        max_requests=2,
        window_seconds=60,
    )

    assert limiter.allow("test") is True
    limiter.record("test")

    assert limiter.allow("test") is True
    limiter.record("test")

    assert limiter.allow("test") is False


def test_bandwidth_limit():
    manager = BandwidthManager()

    manager.set_limit(
        "persona-1",
        BandwidthLimit(
            max_bytes=1000,
        ),
    )

    assert manager.can_transfer("persona-1", 500) is True

    manager.record("persona-1", sent=500, received=0)

    assert manager.can_transfer("persona-1", 600) is False


def test_resource_limits():
    manager = ResourceLimitManager(
        ResourceLimits(
            max_personas=2,
            max_sessions=2,
        )
    )

    manager.increment("personas")

    assert manager.within_limits("personas") is True

    manager.increment("personas")

    assert manager.within_limits("personas") is False


def test_emergency_stop():
    emergency_stop = EmergencyStop()

    assert emergency_stop.allows_activity() is True

    emergency_stop.activate()

    assert emergency_stop.allows_activity() is False

    emergency_stop.reset()

    assert emergency_stop.allows_activity() is True
