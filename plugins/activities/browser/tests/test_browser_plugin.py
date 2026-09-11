from pathlib import Path
import sys

import pytest


PLUGIN_ROOT = Path(__file__).resolve().parents[1]

if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from plugin import (
    BrowserPlugin,
    BrowserRequest,
)


def test_plugin_metadata():
    plugin = BrowserPlugin()

    assert plugin.metadata.id == "activity-browser"
    assert plugin.metadata.name == "Browser Activity Plugin"
    assert plugin.metadata.version == "0.1.0"


def test_plugin_requires_initialization():
    plugin = BrowserPlugin()

    assert plugin.start() is False
    assert plugin.health_check() is False


def test_plugin_lifecycle():
    plugin = BrowserPlugin()

    assert plugin.initialize(context={}) is True
    assert plugin.start() is True
    assert plugin.health_check() is True

    assert plugin.stop() is True
    assert plugin.health_check() is False


def test_create_session():
    plugin = BrowserPlugin()

    plugin.initialize(context={})
    plugin.start()

    session = plugin.create_session(
        persona_id="alex",
    )

    assert session.session_id == "browser-session-0001"
    assert session.persona_id == "alex"
    assert session.active is True
    assert session.pages_visited == 0
    assert session.actions_performed == 0


def test_multiple_sessions_get_unique_ids():
    plugin = BrowserPlugin()

    plugin.initialize(context={})
    plugin.start()

    first = plugin.create_session(persona_id="alex")
    second = plugin.create_session(persona_id="morgan")

    assert first.session_id != second.session_id
    assert first.session_id == "browser-session-0001"
    assert second.session_id == "browser-session-0002"


def test_prepare_navigation():
    plugin = BrowserPlugin(max_pages=10)

    request = plugin.prepare_navigation(
        url="https://example.org",
        persona_id="alex",
    )

    assert isinstance(request, BrowserRequest)
    assert request.url == "https://example.org"
    assert request.persona_id == "alex"
    assert request.max_pages == 10
    assert request.allow_downloads is False
    assert request.allow_uploads is False


def test_navigation_strips_whitespace():
    plugin = BrowserPlugin()

    request = plugin.prepare_navigation(
        "  https://example.org  ",
    )

    assert request.url == "https://example.org"


def test_empty_url_is_rejected():
    plugin = BrowserPlugin()

    with pytest.raises(ValueError):
        plugin.prepare_navigation("")


def test_invalid_scheme_is_rejected():
    plugin = BrowserPlugin()

    with pytest.raises(ValueError):
        plugin.prepare_navigation("ftp://example.org/file")


def test_missing_host_is_rejected():
    plugin = BrowserPlugin()

    with pytest.raises(ValueError):
        plugin.prepare_navigation("https://")


def test_file_uploads_are_disabled():
    request = BrowserRequest(
        url="https://example.org",
        allow_uploads=True,
    )

    with pytest.raises(ValueError):
        request.validate()


def test_page_limit_is_bounded():
    plugin = BrowserPlugin(max_pages=10)

    request = plugin.prepare_navigation(
        "https://example.org",
        max_pages=1000,
    )

    assert request.max_pages == 10


def test_invalid_page_limit_is_rejected():
    plugin = BrowserPlugin()

    with pytest.raises(ValueError):
        plugin.prepare_navigation(
            "https://example.org",
            max_pages=0,
        )


def test_navigation_requires_existing_session():
    plugin = BrowserPlugin()

    plugin.initialize(context={})
    plugin.start()

    result = plugin.navigate(
        session_id="does-not-exist",
        url="https://example.org",
    )

    assert result.success is False
    assert "does not exist" in result.error.lower()


def test_navigation_requires_active_session():
    plugin = BrowserPlugin()

    plugin.initialize(context={})
    plugin.start()

    session = plugin.create_session()
    plugin.stop_session(session.session_id)

    result = plugin.navigate(
        session_id=session.session_id,
        url="https://example.org",
    )

    assert result.success is False
    assert "not active" in result.error.lower()


def test_navigation_increments_page_count():
    plugin = BrowserPlugin(max_pages=2)

    plugin.initialize(context={})
    plugin.start()

    session = plugin.create_session(
        persona_id="alex",
    )

    result = plugin.navigate(
        session_id=session.session_id,
        url="https://example.org",
    )

    assert result.success is True
    assert session.pages_visited == 1


def test_navigation_respects_page_limit():
    plugin = BrowserPlugin(max_pages=1)

    plugin.initialize(context={})
    plugin.start()

    session = plugin.create_session()

    first = plugin.navigate(
        session_id=session.session_id,
        url="https://example.org",
    )

    second = plugin.navigate(
        session_id=session.session_id,
        url="https://example.org/page2",
    )

    assert first.success is True
    assert second.success is False
    assert "page limit" in second.error.lower()


def test_record_action():
    plugin = BrowserPlugin(max_actions=2)

    plugin.initialize(context={})
    plugin.start()

    session = plugin.create_session()

    assert plugin.record_action(session.session_id) is True
    assert plugin.record_action(session.session_id) is True
    assert plugin.record_action(session.session_id) is False

    assert session.actions_performed == 2


def test_stopped_session_cannot_record_action():
    plugin = BrowserPlugin()

    plugin.initialize(context={})
    plugin.start()

    session = plugin.create_session()
    plugin.stop_session(session.session_id)

    assert plugin.record_action(session.session_id) is False


def test_stop_session():
    plugin = BrowserPlugin()

    plugin.initialize(context={})
    plugin.start()

    session = plugin.create_session()

    assert plugin.stop_session(session.session_id) is True
    assert session.active is False


def test_stop_plugin_stops_sessions():
    plugin = BrowserPlugin()

    plugin.initialize(context={})
    plugin.start()

    first = plugin.create_session()
    second = plugin.create_session()

    plugin.stop()

    assert first.active is False
    assert second.active is False


def test_browser_request_rejects_excessive_pages():
    request = BrowserRequest(
        url="https://example.org",
        max_pages=101,
    )

    with pytest.raises(ValueError):
        request.validate()


def test_browser_request_rejects_invalid_url_type():
    plugin = BrowserPlugin()

    with pytest.raises(TypeError):
        plugin.prepare_navigation(123)  # type: ignore[arg-type]
