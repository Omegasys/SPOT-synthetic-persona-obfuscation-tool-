"""SPOT persona-to-Qube mapping."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class PersonaQube:
    """Map one synthetic persona to an isolated Qube."""

    persona_id: str
    qube_name: str

    template: str = "whonix-workstation"

    disposable: bool = False
    persistent: bool = True

    network_mode: str = "whonix"

    enabled: bool = True

    metadata: Dict[str, str] = field(
        default_factory=dict
    )


class PersonaQubeManager:
    """Manage isolation boundaries between personas and Qubes."""

    def __init__(self) -> None:
        self.mappings: Dict[
            str,
            PersonaQube,
        ] = {}

    def assign(
        self,
        persona_id: str,
        qube_name: str,
        template: str = "whonix-workstation",
        disposable: bool = False,
        persistent: bool = True,
        network_mode: str = "whonix",
    ) -> PersonaQube:
        """Assign a persona to a Qube."""
        if persona_id in self.mappings:
            raise ValueError(
                f"Persona already has a Qube: {persona_id}"
            )

        if not persona_id:
            raise ValueError(
                "Persona ID cannot be empty."
            )

        if not qube_name:
            raise ValueError(
                "Qube name cannot be empty."
            )

        if disposable and persistent:
            raise ValueError(
                "A disposable Qube cannot be persistent."
            )

        mapping = PersonaQube(
            persona_id=persona_id,
            qube_name=qube_name,
            template=template,
            disposable=disposable,
            persistent=persistent,
            network_mode=network_mode,
        )

        self.mappings[persona_id] = mapping

        return mapping

    def get(
        self,
        persona_id: str,
    ) -> PersonaQube | None:
        """Return a persona's Qube mapping."""
        return self.mappings.get(persona_id)

    def require(
        self,
        persona_id: str,
    ) -> PersonaQube:
        """Return a mapping or raise an error."""
        mapping = self.get(persona_id)

        if mapping is None:
            raise KeyError(
                f"No Qube assigned to persona: {persona_id}"
            )

        return mapping

    def disable(
        self,
        persona_id: str,
    ) -> None:
        """Disable a persona's Qube mapping."""
        mapping = self.require(persona_id)
        mapping.enabled = False

    def enable(
        self,
        persona_id: str,
    ) -> None:
        """Enable a persona's Qube mapping."""
        mapping = self.require(persona_id)
        mapping.enabled = True

    def remove(
        self,
        persona_id: str,
    ) -> None:
        """Remove a persona mapping."""
        self.require(persona_id)
        del self.mappings[persona_id]

    def active(self) -> List[PersonaQube]:
        """Return enabled persona mappings."""
        return [
            mapping
            for mapping in self.mappings.values()
            if mapping.enabled
        ]

    def qube_for(
        self,
        persona_id: str,
    ) -> str:
        """Return the Qube assigned to a persona."""
        return self.require(persona_id).qube_name

    def persona_for(
        self,
        qube_name: str,
    ) -> str | None:
        """Return the persona assigned to a Qube."""
        for mapping in self.mappings.values():
            if mapping.qube_name == qube_name:
                return mapping.persona_id

        return None
