"""SPOT synthetic browser fingerprint profiles."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class FingerprintProfile:
    """A stable, synthetic browser environment description.

    The purpose of this class is consistency between sessions
    belonging to the same synthetic persona. It is not intended
    to defeat security systems or evade fingerprinting controls.
    """

    browser: str = "generic"
    operating_system: str = "Linux"

    language: str = "en-US"
    timezone: str = "UTC"

    screen_width: int = 1920
    screen_height: int = 1080

    color_depth: int = 24

    user_agent: str = ""

    features: Dict[str, bool] = field(
        default_factory=dict
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def validate(self) -> None:
        """Validate fingerprint parameters."""
        if self.screen_width < 1:
            raise ValueError(
                "screen_width must be positive."
            )

        if self.screen_height < 1:
            raise ValueError(
                "screen_height must be positive."
            )

        if self.color_depth < 1:
            raise ValueError(
                "color_depth must be positive."
            )

        if not self.language:
            raise ValueError(
                "language cannot be empty."
            )

        if not self.timezone:
            raise ValueError(
                "timezone cannot be empty."
            )

    def set_feature(
        self,
        name: str,
        enabled: bool,
    ) -> None:
        """Set a synthetic browser feature."""
        self.features[name] = bool(enabled)

    def feature_enabled(
        self,
        name: str,
    ) -> bool:
        """Return whether a feature is enabled."""
        return self.features.get(
            name,
            False,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert the fingerprint to a dictionary."""
        return {
            "browser": self.browser,
            "operating_system": self.operating_system,
            "language": self.language,
            "timezone": self.timezone,
            "screen_width": self.screen_width,
            "screen_height": self.screen_height,
            "color_depth": self.color_depth,
            "user_agent": self.user_agent,
            "features": dict(self.features),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "FingerprintProfile":
        """Create a fingerprint profile from data."""
        profile = cls(
            browser=str(
                data.get("browser", "generic")
            ),
            operating_system=str(
                data.get(
                    "operating_system",
                    "Linux",
                )
            ),
            language=str(
                data.get(
                    "language",
                    "en-US",
                )
            ),
            timezone=str(
                data.get(
                    "timezone",
                    "UTC",
                )
            ),
            screen_width=int(
                data.get(
                    "screen_width",
                    1920,
                )
            ),
            screen_height=int(
                data.get(
                    "screen_height",
                    1080,
                )
            ),
            color_depth=int(
                data.get(
                    "color_depth",
                    24,
                )
            ),
            user_agent=str(
                data.get(
                    "user_agent",
                    "",
                )
            ),
            features=dict(
                data.get(
                    "features",
                    {},
                )
            ),
            metadata=dict(
                data.get(
                    "metadata",
                    {},
                )
            ),
        )

        profile.validate()
        return profile
