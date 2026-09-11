from pathlib import Path

import pytest

from spot.browser.manager import BrowserManager
from spot.browser.profiles import BrowserProfile


def test_browser_profiles_are_separate(tmp_path):
    manager = BrowserManager()

    profile_a = manager.create_profile(
        BrowserProfile(
            id="persona-a",
            path=tmp_path / "persona-a",
            persistent=True,
            allow_personal_profile_import=False,
            allow_credentials=False,
        )
    )

    profile_b = manager.create_profile(
        BrowserProfile(
            id="persona-b",
            path=tmp_path / "persona-b",
            persistent=True,
            allow_personal_profile_import=False,
            allow_credentials=False,
        )
    )

    assert profile_a.path != profile_b.path
    assert profile_a.id != profile_b.id


def test_browser_profiles_do_not_share_state_directory(tmp_path):
    manager = BrowserManager()

    profile_a = manager.create_profile(
        BrowserProfile(
            id="persona-a",
            path=tmp_path / "persona-a",
        )
    )

    profile_b = manager.create_profile(
        BrowserProfile(
            id="persona-b",
            path=tmp_path / "persona-b",
        )
    )

    assert profile_a.path != profile_b.path
    assert profile_a.path.parent == tmp_path
    assert profile_b.path.parent == tmp_path


def test_personal_profile_import_is_disabled(tmp_path):
    profile = BrowserProfile(
        id="persona",
        path=tmp_path / "profile",
        allow_personal_profile_import=False,
        allow_credentials=False,
    )

    assert profile.allow_personal_profile_import is False
    assert profile.allow_credentials is False


def test_personal_profile_import_is_rejected(tmp_path):
    profile = BrowserProfile(
        id="persona",
        path=tmp_path / "profile",
        allow_personal_profile_import=True,
    )

    with pytest.raises(ValueError):
        profile.validate()


def test_browser_manager_can_remove_profile(tmp_path):
    manager = BrowserManager()

    manager.create_profile(
        BrowserProfile(
            id="persona",
            path=tmp_path / "persona",
        )
    )

    assert manager.get_profile("persona") is not None

    manager.remove_profile("persona")

    assert manager.get_profile("persona") is None


def test_browser_sessions_are_isolated_by_profile(tmp_path):
    manager = BrowserManager()

    manager.create_profile(
        BrowserProfile(
            id="persona-a",
            path=tmp_path / "persona-a",
        )
    )

    manager.create_profile(
        BrowserProfile(
            id="persona-b",
            path=tmp_path / "persona-b",
        )
    )

    session_a = manager.start_session("persona-a")
    session_b = manager.start_session("persona-b")

    assert session_a.profile_id != session_b.profile_id

    manager.stop_session(session_a.id)
    manager.stop_session(session_b.id)
