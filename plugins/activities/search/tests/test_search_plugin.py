from pathlib import Path
import sys

import pytest


PLUGIN_ROOT = Path(__file__).resolve().parents[1]

if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from plugin import SearchPlugin, SearchRequest


def test_plugin_metadata():
    plugin = SearchPlugin()

    assert plugin.metadata.id == "activity-search"
    assert plugin.metadata.name == "Search Activity Plugin"
    assert plugin.metadata.version == "0.1.0"


def test_plugin_requires_initialization():
    plugin = SearchPlugin()

    assert plugin.start() is False
    assert plugin.health_check() is False


def test_plugin_lifecycle():
    plugin = SearchPlugin()

    assert plugin.initialize(context={}) is True
    assert plugin.start() is True
    assert plugin.health_check() is True

    assert plugin.stop() is True
    assert plugin.health_check() is False


def test_prepare_search():
    plugin = SearchPlugin(max_results=10)

    request = plugin.prepare_search(
        query="Linux networking",
        persona_id="alex",
    )

    assert isinstance(request, SearchRequest)
    assert request.query == "Linux networking"
    assert request.persona_id == "alex"
    assert request.max_results == 10


def test_prepare_search_strips_whitespace():
    plugin = SearchPlugin()

    request = plugin.prepare_search("  Linux  ")

    assert request.query == "Linux"


def test_empty_query_is_rejected():
    plugin = SearchPlugin()

    with pytest.raises(ValueError):
        plugin.prepare_search("")


def test_whitespace_query_is_rejected():
    plugin = SearchPlugin()

    with pytest.raises(ValueError):
        plugin.prepare_search("   ")


def test_query_length_is_limited():
    plugin = SearchPlugin(max_query_length=20)

    with pytest.raises(ValueError):
        plugin.prepare_search("a" * 21)


def test_result_limit_is_bounded():
    plugin = SearchPlugin(max_results=10)

    request = plugin.prepare_search(
        query="test",
        max_results=1000,
    )

    assert request.max_results == 10


def test_invalid_result_limit_is_rejected():
    plugin = SearchPlugin()

    with pytest.raises(ValueError):
        plugin.prepare_search(
            query="test",
            max_results=0,
        )


def test_non_string_query_is_rejected():
    plugin = SearchPlugin()

    with pytest.raises(TypeError):
        plugin.prepare_search(123)  # type: ignore[arg-type]


def test_execute_requires_running_plugin():
    plugin = SearchPlugin()

    result = plugin.execute("Linux")

    assert result.success is False
    assert "not running" in result.error.lower()


def test_execute_does_not_make_network_request():
    plugin = SearchPlugin()

    plugin.initialize(context={})
    plugin.start()

    result = plugin.execute(
        query="Linux networking",
        persona_id="alex",
    )

    assert result.success is True
    assert result.request.query == "Linux networking"

    # The generic plugin prepares activity but does not contact
    # an external search provider.
    assert result.results == []


def test_metadata_is_preserved():
    plugin = SearchPlugin()

    request = plugin.prepare_search(
        query="Linux",
        persona_id="alex",
        metadata={
            "synthetic": True,
            "category": "technology",
        },
    )

    assert request.metadata["synthetic"] is True
    assert request.metadata["category"] == "technology"


def test_search_request_validation():
    request = SearchRequest(
        query="test",
        max_results=5,
    )

    request.validate()


def test_search_request_rejects_empty_query():
    request = SearchRequest(
        query="",
        max_results=5,
    )

    with pytest.raises(ValueError):
        request.validate()


def test_search_request_rejects_excessive_results():
    request = SearchRequest(
        query="test",
        max_results=101,
    )

    with pytest.raises(ValueError):
        request.validate()
