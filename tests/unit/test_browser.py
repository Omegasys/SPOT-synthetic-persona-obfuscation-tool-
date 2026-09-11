from pathlib import Path

import pytest

from spot.browser.profiles import BrowserProfile
from spot.browser.sessions import BrowserSession
from spot.browser.automation import AutomationPolicy


def test_browser_profile_is_isolated(tmp_path):
    profile = BrowserProfile(
        id="test-profile",
        path=tmp_path / "profile",
        persistent=True,
        allow_personal_profile_import=False,
        allow_credentials=False,
    )

    assert profile.allow_personal_profile_import is False
    assert profile.allow_credentials is False


def test_browser_profile_validation(tmp_path):
    profile = BrowserProfile(
        id="test-profile",
        path=tmp_path / "profile",
    )

    assert profile.validate() is True


def test_browser_profile_rejects_personal_import(tmp_path):
    profile = BrowserProfile(
        id="test-profile",
        path=tmp_path / "profile",
        allow_personal_profile_import=True,
    )

    with pytest.raises(ValueError):
        profile.validate()


def test_browser_session_starts_and_stops():
    session = BrowserSession(
        id="test-session",
        profile_id="test-profile",
    )

    session.start()

    assert session.active is True

    session.stop()

    assert session.active is False


def test_browser_session_page_count():
    session = BrowserSession(
        id="test-session",
        profile_id="test-profile",
    )

    session.start()

    session.record_page()
    session.record_page()

    assert session.page_count == 2


def test_automation_policy_defaults_are_restrictive():
    policy = AutomationPolicy()

    assert policy.allow_uploads is False
    assert policy.allow_downloads is False
    assert policy.allow_navigation is True


def test_automation_policy_allowed_domains():
    policy = AutomationPolicy(
        allowed_domains=["example.com"],
    )

    assert policy.is_domain_allowed("example.com") is True
    assert policy.is_domain_allowed("other.example") is False
