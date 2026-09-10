"""SPOT Qubes template definitions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class QubeTemplate:
    """Definition of a Qubes template or base environment."""

    name: str
    description: str = ""

    disposable: bool = False
    netvm: str | None = None

    tags: List[str] = field(
        default_factory=list
    )

    properties: Dict[str, str] = field(
        default_factory=dict
    )

    enabled: bool = True


class QubeTemplateManager:
    """Manage SPOT-approved Qube templates."""

    DEFAULT_TEMPLATES = {
        "fedora": QubeTemplate(
            name="fedora",
            description="Generic Fedora-based SPOT environment.",
        ),
        "debian": QubeTemplate(
            name="debian",
            description="Generic Debian-based SPOT environment.",
        ),
        "whonix-workstation": QubeTemplate(
            name="whonix-workstation",
            description=(
                "Whonix workstation environment intended "
                "to route through a Whonix gateway."
            ),
            netvm="sys-whonix",
            tags=["whonix", "tor"],
        ),
    }

    def __init__(
        self,
        templates: Dict[str, QubeTemplate] | None = None,
    ) -> None:
        self.templates = dict(
            templates
            or self.DEFAULT_TEMPLATES
        )

    def add(
        self,
        template: QubeTemplate,
    ) -> None:
        """Add a template."""
        if template.name in self.templates:
            raise ValueError(
                f"Template already exists: {template.name}"
            )

        self.templates[template.name] = template

    def get(
        self,
        name: str,
    ) -> QubeTemplate | None:
        """Return a template."""
        return self.templates.get(name)

    def require(
        self,
        name: str,
    ) -> QubeTemplate:
        """Return a template or raise an error."""
        template = self.get(name)

        if template is None:
            raise KeyError(
                f"Unknown Qube template: {name}"
            )

        if not template.enabled:
            raise PermissionError(
                f"Qube template is disabled: {name}"
            )

        return template

    def remove(
        self,
        name: str,
    ) -> None:
        """Remove a template."""
        if name not in self.templates:
            raise KeyError(
                f"Unknown Qube template: {name}"
            )

        del self.templates[name]

    def available(self) -> List[str]:
        """Return enabled template names."""
        return sorted(
            template.name
            for template in self.templates.values()
            if template.enabled
        )
