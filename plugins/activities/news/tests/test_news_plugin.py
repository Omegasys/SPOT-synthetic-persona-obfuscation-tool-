from pathlib import Path
import sys

import pytest


PLUGIN_ROOT = Path(__file__).resolve().parents[1]

if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from plugin import (
    NewsArticle,
    NewsPlugin,
    NewsRequest,
)


def test_plugin_metadata():
    plugin = NewsPlugin()

    assert plugin.metadata.id == "activity-news"
    assert plugin.metadata.name == "News Activity Plugin"
    assert plugin.metadata.version == "0.1.0"


def test_plugin_requires_initialization():
    plugin = NewsPlugin()

    assert plugin.start() is False
    assert plugin.health_check() is False


def test_plugin_lifecycle():
    plugin = NewsPlugin()

    assert plugin.initialize(context={}) is True
    assert plugin.start() is True
    assert plugin.health_check() is True

    assert plugin.stop() is True
    assert plugin.health_check() is False


def test_prepare_news():
    plugin = NewsPlugin(
        max_articles=5,
        max_sources=3,
    )

    request = plugin.prepare_news(
        topic="technology",
        persona_id="alex",
    )

    assert isinstance(request, NewsRequest)
    assert request.topic == "technology"
    assert request.persona_id == "alex"
    assert request.max_articles == 5
    assert request.max_sources == 3


def test_prepare_news_strips_whitespace():
    plugin = NewsPlugin()

    request = plugin.prepare_news(
        "  technology  ",
    )

    assert request.topic == "technology"


def test_empty_topic_is_rejected():
    plugin = NewsPlugin()

    with pytest.raises(ValueError):
        plugin.prepare_news("")


def test_whitespace_topic_is_rejected():
    plugin = NewsPlugin()

    with pytest.raises(ValueError):
        plugin.prepare_news("   ")


def test_topic_length_is_limited():
    plugin = NewsPlugin(max_topic_length=20)

    with pytest.raises(ValueError):
        plugin.prepare_news("a" * 21)


def test_article_limit_is_bounded():
    plugin = NewsPlugin(max_articles=5)

    request = plugin.prepare_news(
        topic="science",
        max_articles=1000,
    )

    assert request.max_articles == 5


def test_source_limit_is_bounded():
    plugin = NewsPlugin(max_sources=3)

    request = plugin.prepare_news(
        topic="science",
        max_sources=1000,
    )

    assert request.max_sources == 3


def test_invalid_article_limit_is_rejected():
    plugin = NewsPlugin()

    with pytest.raises(ValueError):
        plugin.prepare_news(
            topic="science",
            max_articles=0,
        )


def test_invalid_source_limit_is_rejected():
    plugin = NewsPlugin()

    with pytest.raises(ValueError):
        plugin.prepare_news(
            topic="science",
            max_sources=0,
        )


def test_non_string_topic_is_rejected():
    plugin = NewsPlugin()

    with pytest.raises(TypeError):
        plugin.prepare_news(123)  # type: ignore[arg-type]


def test_execute_requires_running_plugin():
    plugin = NewsPlugin()

    result = plugin.execute("technology")

    assert result.success is False
    assert "not running" in result.error.lower()


def test_execute_does_not_make_network_request():
    plugin = NewsPlugin()

    plugin.initialize(context={})
    plugin.start()

    result = plugin.execute(
        topic="technology",
        persona_id="alex",
    )

    assert result.success is True
    assert result.request.topic == "technology"

    # The provider-neutral implementation does not contact
    # an external news service.
    assert result.articles == []


def test_metadata_is_preserved():
    plugin = NewsPlugin()

    request = plugin.prepare_news(
        topic="science",
        persona_id="alex",
        metadata={
            "synthetic": True,
            "category": "science",
        },
    )

    assert request.metadata["synthetic"] is True
    assert request.metadata["category"] == "science"


def test_news_request_validation():
    request = NewsRequest(
        topic="technology",
        max_articles=5,
        max_sources=3,
    )

    request.validate()


def test_news_request_rejects_empty_topic():
    request = NewsRequest(
        topic="",
        max_articles=5,
        max_sources=3,
    )

    with pytest.raises(ValueError):
        request.validate()


def test_news_request_rejects_excessive_articles():
    request = NewsRequest(
        topic="technology",
        max_articles=51,
        max_sources=3,
    )

    with pytest.raises(ValueError):
        request.validate()


def test_news_request_rejects_excessive_sources():
    request = NewsRequest(
        topic="technology",
        max_articles=5,
        max_sources=21,
    )

    with pytest.raises(ValueError):
        request.validate()


def test_news_article():
    article = NewsArticle(
        title="Example Technology Article",
        source="Example Source",
        url="https://example.org/article",
        topic="technology",
    )

    assert article.title == "Example Technology Article"
    assert article.source == "Example Source"
    assert article.url == "https://example.org/article"
    assert article.topic == "technology"
