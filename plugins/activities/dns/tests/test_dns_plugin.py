from pathlib import Path
import sys

import pytest


PLUGIN_ROOT = Path(__file__).resolve().parents[1]

if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from plugin import (
    DNSPlugin,
    DNSRequest,
    DNSRecordType,
)


def test_plugin_metadata():
    plugin = DNSPlugin()

    assert plugin.metadata.id == "activity-dns"
    assert plugin.metadata.name == "DNS Activity Plugin"
    assert plugin.metadata.version == "0.1.0"


def test_plugin_requires_initialization():
    plugin = DNSPlugin()

    assert plugin.start() is False
    assert plugin.health_check() is False


def test_plugin_lifecycle():
    plugin = DNSPlugin()

    assert plugin.initialize(context={}) is True
    assert plugin.start() is True
    assert plugin.health_check() is True

    assert plugin.stop() is True
    assert plugin.health_check() is False


@pytest.mark.parametrize(
    "record_type",
    [
        DNSRecordType.A,
        DNSRecordType.AAAA,
        DNSRecordType.CNAME,
        DNSRecordType.MX,
        DNSRecordType.NS,
        DNSRecordType.TXT,
    ],
)
def test_supported_record_types(record_type):
    plugin = DNSPlugin()

    request = plugin.prepare_query(
        domain="example.org",
        record_type=record_type,
    )

    assert isinstance(request, DNSRequest)
    assert request.record_type == record_type


def test_string_record_type_is_supported():
    plugin = DNSPlugin()

    request = plugin.prepare_query(
        domain="example.org",
        record_type="A",
    )

    assert request.record_type == DNSRecordType.A


def test_string_record_type_is_case_insensitive():
    plugin = DNSPlugin()

    request = plugin.prepare_query(
        domain="example.org",
        record_type="aaaa",
    )

    assert request.record_type == DNSRecordType.AAAA


def test_invalid_record_type_is_rejected():
    plugin = DNSPlugin()

    with pytest.raises(ValueError):
        plugin.prepare_query(
            domain="example.org",
            record_type="INVALID",
        )


def test_prepare_query():
    plugin = DNSPlugin()

    request = plugin.prepare_query(
        domain="example.org",
        record_type=DNSRecordType.A,
        persona_id="alex",
    )

    assert request.domain == "example.org"
    assert request.record_type == DNSRecordType.A
    assert request.persona_id == "alex"


def test_domain_trailing_dot_is_removed():
    plugin = DNSPlugin()

    request = plugin.prepare_query(
        domain="example.org.",
    )

    assert request.domain == "example.org"


def test_domain_whitespace_is_removed():
    plugin = DNSPlugin()

    request = plugin.prepare_query(
        domain="  example.org  ",
    )

    assert request.domain == "example.org"


def test_empty_domain_is_rejected():
    plugin = DNSPlugin()

    with pytest.raises(ValueError):
        plugin.prepare_query("")


def test_invalid_domain_is_rejected():
    plugin = DNSPlugin()

    with pytest.raises(ValueError):
        plugin.prepare_query("not a valid domain")


def test_domain_with_empty_label_is_rejected():
    plugin = DNSPlugin()

    with pytest.raises(ValueError):
        plugin.prepare_query("example..org")


def test_domain_with_invalid_character_is_rejected():
    plugin = DNSPlugin()

    with pytest.raises(ValueError):
        plugin.prepare_query("example_org")


def test_domain_too_long_is_rejected():
    plugin = DNSPlugin()

    domain = ("a" * 63) + "." + ("b" * 63) + "." + ("c" * 63) + "." + (
        "d" * 63
    ) + ".com"

    with pytest.raises(ValueError):
        plugin.prepare_query(domain)


def test_non_string_domain_is_rejected():
    plugin = DNSPlugin()

    with pytest.raises(TypeError):
        plugin.prepare_query(123)  # type: ignore[arg-type]


def test_execute_requires_running_plugin():
    plugin = DNSPlugin()

    result = plugin.execute("example.org")

    assert result.success is False
    assert "not running" in result.error.lower()


def test_execute_is_bounded():
    plugin = DNSPlugin(max_queries=2)

    plugin.initialize(context={})
    plugin.start()

    first = plugin.execute("example.org")
    second = plugin.execute("example.net")
    third = plugin.execute("example.com")

    assert first.success is True
    assert second.success is True
    assert third.success is False
    assert "query limit" in third.error.lower()


def test_reset_clears_query_limit():
    plugin = DNSPlugin(max_queries=1)

    plugin.initialize(context={})
    plugin.start()

    first = plugin.execute("example.org")
    assert first.success is True

    second = plugin.execute("example.net")
    assert second.success is False

    plugin.reset()

    third = plugin.execute("example.com")
    assert third.success is True


def test_execute_does_not_perform_dns_resolution():
    plugin = DNSPlugin()

    plugin.initialize(context={})
    plugin.start()

    result = plugin.execute("example.org")

    assert result.success is True

    # Actual DNS answers are intentionally empty because resolution
    # belongs to SPOT's network layer.
    assert result.answers == []


def test_metadata_is_preserved():
    plugin = DNSPlugin()

    request = plugin.prepare_query(
        domain="example.org",
        metadata={
            "synthetic": True,
            "category": "technology",
        },
    )

    assert request.metadata["synthetic"] is True
    assert request.metadata["category"] == "technology"


def test_dns_request_validation():
    request = DNSRequest(
        domain="example.org",
        record_type=DNSRecordType.A,
    )

    request.validate()


def test_private_destination_is_blocked():
    plugin = DNSPlugin(
        block_private_targets=True,
    )

    assert plugin.can_use_destination("192.168.1.1") is False


def test_loopback_destination_is_blocked():
    plugin = DNSPlugin(
        block_private_targets=True,
    )

    assert plugin.can_use_destination("127.0.0.1") is False


def test_link_local_destination_is_blocked():
    plugin = DNSPlugin(
        block_private_targets=True,
    )

    assert plugin.can_use_destination("169.254.1.1") is False


def test_multicast_destination_is_blocked():
    plugin = DNSPlugin(
        block_private_targets=True,
    )

    assert plugin.can_use_destination("224.0.0.1") is False


def test_unspecified_destination_is_blocked():
    plugin = DNSPlugin(
        block_private_targets=True,
    )

    assert plugin.can_use_destination("0.0.0.0") is False


def test_public_destination_is_allowed():
    plugin = DNSPlugin(
        block_private_targets=True,
    )

    assert plugin.can_use_destination("1.1.1.1") is True


def test_private_destination_can_be_allowed_when_policy_disabled():
    plugin = DNSPlugin(
        block_private_targets=False,
    )

    assert plugin.can_use_destination("192.168.1.1") is True


def test_restricted_record_types():
    plugin = DNSPlugin(
        allowed_record_types={DNSRecordType.A},
    )

    request = plugin.prepare_query(
        domain="example.org",
        record_type=DNSRecordType.A,
    )

    assert request.record_type == DNSRecordType.A

    with pytest.raises(ValueError):
        plugin.prepare_query(
            domain="example.org",
            record_type=DNSRecordType.MX,
        )


def test_dns_request_rejects_excessive_domain_length():
    request = DNSRequest(
        domain="a" * 254,
    )

    with pytest.raises(ValueError):
        request.validate()
