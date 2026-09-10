"""SPOT browser manager."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .profiles import BrowserProfile
from .sessions import BrowserSession


@dataclass
class BrowserManager:
    """Manage isolated browser profiles and sessions."""

    profiles: Dict[str, BrowserProfile]
    sessions: Dict[str, BrowserSession]

    def __init__(self) -> None:
        self.profiles = {}
        self.sessions = {}

    def create_profile(
        self,
        profile: BrowserProfile,
    ) -> BrowserProfile:
        """Register a browser profile."""
        if profile.profile_id in self.profiles:
            raise ValueError(
                f"Profile already exists: {profile.profile_id}"
            )

        self.profiles[profile.profile_id] = profile
        return profile

    def get_profile(
        self,
        profile_id: str,
    ) -> BrowserProfile:
        """Return a browser profile."""
        try:
            return self.profiles[profile_id]
        except KeyError:
            raise KeyError(
                f"Unknown browser profile: {profile_id}"
            ) from None

    def remove_profile(
        self,
        profile_id: str,
    ) -> None:
        """Remove a browser profile."""
        if any(
            session.profile_id == profile_id
            for session in self.sessions.values()
            if session.active
        ):
            raise RuntimeError(
                "Cannot remove a profile with an active session."
            )

        self.profiles.pop(profile_id, None)

    def start_session(
        self,
        profile_id: str,
    ) -> BrowserSession:
        """Create and start an isolated browser session."""
        profile = self.get_profile(profile_id)

        if not profile.enabled:
            raise RuntimeError(
                "Browser profile is disabled."
            )

        session = BrowserSession(
            profile_id=profile.profile_id,
        )
        session.start()

        self.sessions[session.session_id] = session

        return session

    def stop_session(
        self,
        session_id: str,
    ) -> None:
        """Stop a browser session."""
        session = self.sessions.get(session_id)

        if session is None:
            return

        session.stop()

    def active_sessions(self) -> List[BrowserSession]:
        """Return active browser sessions."""
        return [
            session
            for session in self.sessions.values()
            if session.active
        ]

    def stop_all(self) -> None:
        """Stop all active browser sessions."""
        for session in self.sessions.values():
            if session.active:
                session.stop()

    def clear_stopped_sessions(self) -> None:
        """Remove stopped sessions from memory."""
        self.sessions = {
            session_id: session
            for session_id, session in self.sessions.items()
            if session.active
        }
