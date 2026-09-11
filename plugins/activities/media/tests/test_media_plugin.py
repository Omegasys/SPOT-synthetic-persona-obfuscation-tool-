from pathlib import Path
import sys

import pytest


PLUGIN_ROOT = Path(__file__).resolve().parents[1]

if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from plugin import (
    MediaItem,
    MediaPlugin,
    MediaRequest,
    MediaType,
)


def test_plugin_metadata():
    plugin = MediaPlugin()

    assert plugin.metadata.id == "activity-media"
    assert plugin.metadata.name == "Media Activity Plugin"
    assert plugin.metadata.version == "0.1.0"


def test_plugin_requires_initialization():
    plugin = MediaPlugin()

    assert plugin.start() is False
    assert plugin.health_check() is False


def test_plugin_lifecycle():
    plugin = MediaPlugin()

    assert plugin.initialize(context={}) is True
    assert plugin.start() is True
    assert plugin.health_check() is True

    assert plugin.stop() is True
    assert plugin.health_check() is False


@pytest.mark.parametrize(
    "media_type",
    [
        MediaType.VIDEO,
        MediaType.AUDIO,
        MediaType.MUSIC,
        MediaType.PODCAST,
        MediaType.IMAGE,
        MediaType.STREAM,
    ],
)
def test_supported_media_types(media_type):
    plugin = MediaPlugin()

    request = plugin.prepare_media(
        media_type=media_type,
        target="example",
    )

    assert request.media_type == media_type


def test_string_media_type_is_supported():
    plugin = MediaPlugin()

    request = plugin.prepare_media(
        media_type="video",
        target="example",
    )

    assert request.media_type == MediaType.VIDEO


def test_string_media_type_is_case_insensitive():
    plugin = MediaPlugin()

    request = plugin.prepare_media(
        media_type="VIDEO",
        target="example",
    )

    assert request.media_type == MediaType.VIDEO


def test_invalid_media_type_is_rejected():
    plugin = MediaPlugin()

    with pytest.raises(ValueError):
        plugin.prepare_media(
            media_type="unknown",
            target="example",
        )


def test_prepare_media():
    plugin = MediaPlugin(
        max_duration_seconds=3600,
        max_items=5,
    )

    request = plugin.prepare_media(
        media_type=MediaType.VIDEO,
        target="technology",
        persona_id="alex",
    )

    assert isinstance(request, MediaRequest)
    assert request.media_type == MediaType.VIDEO
    assert request.target == "technology"
    assert request.persona_id == "alex"
    assert request.duration_seconds == 300
    assert request.max_items == 5


def test_prepare_media_strips_target():
    plugin = MediaPlugin()

    request = plugin.prepare_media(
        media_type="video",
        target="  technology  ",
    )

    assert request.target == "technology"


def test_empty_target_is_rejected():
    plugin = MediaPlugin()

    with pytest.raises(ValueError):
        plugin.prepare_media(
            media_type="video",
            target="",
        )


def test_target_length_is_limited():
    plugin = MediaPlugin(max_target_length=20)

    with pytest.raises(ValueError):
        plugin.prepare_media(
            media_type="video",
            target="a" * 21,
        )


def test_duration_is_bounded():
    plugin = MediaPlugin(
        max_duration_seconds=600,
    )

    request = plugin.prepare_media(
        media_type="video",
        target="example",
        duration_seconds=5000,
    )

    assert request.duration_seconds == 600


def test_item_count_is_bounded():
    plugin = MediaPlugin(max_items=5)

    request = plugin.prepare_media(
        media_type="video",
        target="example",
        max_items=1000,
    )

    assert request.max_items == 5


def test_invalid_duration_is_rejected():
    plugin = MediaPlugin()

    with pytest.raises(ValueError):
        plugin.prepare_media(
            media_type="video",
            target="example",
            duration_seconds=0,
        )


def test_invalid_item_count_is_rejected():
    plugin = MediaPlugin()

    with pytest.raises(ValueError):
        plugin.prepare_media(
            media_type="video",
            target="example",
            max_items=0,
        )


def test_non_string_target_is_rejected():
    plugin = MediaPlugin()

    with pytest.raises(TypeError):
        plugin.prepare_media(
            media_type="video",
            target=123,  # type: ignore[arg-type]
        )


def test_execute_requires_running_plugin():
    plugin = MediaPlugin()

    result = plugin.execute(
        media_type="video",
        target="example",
    )

    assert result.success is False
    assert "not running" in result.error.lower()


def test_execute_does_not_make_network_request():
    plugin = MediaPlugin()

    plugin.initialize(context={})
    plugin.start()

    result = plugin.execute(
        media_type="video",
        target="technology",
        persona_id="alex",
    )

    assert result.success is True
    assert result.request.target == "technology"
    assert result.items == []


def test_metadata_is_preserved():
    plugin = MediaPlugin()

    request = plugin.prepare_media(
        media_type="music",
        target="electronic music",
        persona_id="alex",
        metadata={
            "synthetic": True,
            "category": "music",
        },
    )

    assert request.metadata["synthetic"] is True
    assert request.metadata["category"] == "music"


def test_media_request_validation():
    request = MediaRequest(
        media_type=MediaType.VIDEO,
        target="example",
        duration_seconds=300,
        max_items=5,
    )

    request.validate()


def test_media_request_rejects_excessive_duration():
    request = MediaRequest(
        media_type=MediaType.VIDEO,
        target="example",
        duration_seconds=3601,
        max_items=5,
    )

    with pytest.raises(ValueError):
        request.validate()


def test_media_request_rejects_excessive_items():
    request = MediaRequest(
        media_type=MediaType.VIDEO,
        target="example",
        duration_seconds=300,
        max_items=51,
    )

    with pytest.raises(ValueError):
        request.validate()


def test_media_item():
    item = MediaItem(
        title="Example Video",
        media_type=MediaType.VIDEO,
        source="Example Source",
        url="https://example.org/video",
        duration_seconds=300,
    )

    assert item.title == "Example Video"
    assert item.media_type == MediaType.VIDEO
    assert item.source == "Example Source"
    assert item.url == "https://example.org/video"
    assert item.duration_seconds == 300
