"""SPOT Whonix routing configuration."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class WhonixConfig:
    """Configuration for Qubes/Whonix network routing."""

    enabled: bool = True

    gateway_name: str = "sys-whonix"
    workstation_name: str = "anon-whonix"

    require_gateway: bool = True
    require_tor: bool = True

    fail_closed: bool = True
    allow_direct_fallback: bool = False

    health_check_timeout: int = 30

    def validate(self) -> None:
        """Validate Whonix security settings."""
        if not self.gateway_name:
            raise ValueError(
                "Whonix gateway name cannot be empty."
            )

        if not self.workstation_name:
            raise ValueError(
                "Whonix workstation name cannot be empty."
            )

        if self.health_check_timeout < 1:
            raise ValueError(
                "Health-check timeout must be at least 1 second."
            )

        if (
            self.fail_closed
            and self.allow_direct_fallback
        ):
            raise ValueError(
                "Direct fallback cannot be enabled "
                "when Whonix fail-closed mode is active."
            )

        if self.require_tor:
            self.allow_direct_fallback = False

    def expected_gateway(self) -> str:
        """Return the expected Whonix gateway."""
        return self.gateway_name

    def expected_workstation(self) -> str:
        """Return the expected Whonix workstation."""
        return self.workstation_name

    def routing_requirements(self) -> dict[str, object]:
        """Return required Whonix routing conditions."""
        return {
            "gateway": self.gateway_name,
            "workstation": self.workstation_name,
            "require_gateway": self.require_gateway,
            "require_tor": self.require_tor,
            "fail_closed": self.fail_closed,
            "direct_fallback": self.allow_direct_fallback,
        }
