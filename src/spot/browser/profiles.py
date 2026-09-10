"""SPOT isolated browser profiles."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class BrowserProfile:
    """Configuration for an isolated synthetic browser profile."""

    profile_id: str
    persona_id: str

    browser_name: str = "default"
    enabled: bool = True

    profile_path: str = ""
    isolated: bool = True

    allow_extensions: bool = False
    allow_personal_profile_import: bool = False
    allow_credentials: bool = False

    persistent: bool = True
    cleanup_on_close: bool = False

    settings: Dict[str, Any] = field(
        default_factory=dict
    )

    def validate(self) -> None:
        """Validate security-sensitive profile settings."""
        if not self.profile_id:
            raise ValueError(
                "profile_id cannot be empty."
            )

        if not self.persona_id:
            raise ValueError(
                "persona_id cannot be empty."
            )

        if not self.isolated:
            raise ValueError(
                "SPOT browser profiles must be isolated."
            )

        if self.allow_personal_profile_import:
            raise ValueError(
                "Personal browser profile import is not allowed."
            )

        if self.allow_credentials:
            raise ValueError(
                "Credential storage is not allowed."
            )

    def enable(self) -> None:
        """Enable the profile."""
        self.validate()
        self.enabled = True

    def disable(self) -> None:
        """Disable the profile."""
        self.enabled = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert the profile to a dictionary."""
        return {
            "profile_id": self.profile_id,
            "persona_id": self.persona_id,
            "browser_name": self.browser_name,
            "enabled": self.enabled,
            "profile_path": self.profile_path,
            "isolated": self.isolated,
            "allow_extensions": self.allow_extensions,
            "allow_personal_profile_import": (
                self.allow_personal_profile_import
            ),
            "allow_credentials": self.allow_credentials,
            "persistent": self.persistent,
            "cleanup_on_close": self.cleanup_on_close,
            "settings": dict(self.settings),
        }

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "BrowserProfile":
        """Create a profile from configuration data."""
        profile = cls(
            profile_id=str(data["profile_id"]),
            persona_id=str(data["persona_id"]),
            browser_name=str(
                data.get("browser_name", "default")
            ),
            enabled=bool(
                data.get("enabled", True)
            ),
            profile_path=str(
                data.get("profile_path", "")
            ),
            isolated=bool(
                data.get("isolated", True)
            ),
            allow_extensions=bool(
                data.get("allow_extensions", False)
            ),
            allow_personal_profile_import=bool(
                data.get(
                    "allow_personal_profile_import",
                    False,
                )
            ),
            allow_credentials=bool(
                data.get("allow_credentials", False)
            ),
            persistent=bool(
                data.get("persistent", True)
            ),
            cleanup_on_close=bool(
                data.get("cleanup_on_close", False)
            ),
            settings=dict(
                data.get("settings", {})
            ),
        )

        profile.validate()
        return profile
