"""SPOT persona manager."""

from **future** import annotations

from typing import Dict, Iterable

from .persona import Persona

class PersonaManager:
"""Create, store, retrieve, and manage SPOT personas."""

```
def __init__(self) -> None:
    self._personas: Dict[str, Persona] = {}

@property
def personas(self) -> Dict[str, Persona]:
    """Return the currently registered personas."""
    return dict(self._personas)

def add(self, persona: Persona) -> None:
    """Register a persona."""
    if persona.id in self._personas:
        raise ValueError(
            f"Persona already exists: {persona.id}"
        )

    self._personas[persona.id] = persona

def remove(self, persona_id: str) -> Persona:
    """Remove and return a persona."""
    try:
        return self._personas.pop(persona_id)
    except KeyError as exc:
        raise KeyError(
            f"Persona not found: {persona_id}"
        ) from exc

def get(self, persona_id: str) -> Persona | None:
    """Return a persona by ID."""
    return self._personas.get(persona_id)

def require(self, persona_id: str) -> Persona:
    """Return a persona or raise an error."""
    persona = self.get(persona_id)

    if persona is None:
        raise KeyError(f"Persona not found: {persona_id}")

    return persona

def enable(self, persona_id: str) -> None:
    """Enable a persona."""
    self.require(persona_id).enable()

def disable(self, persona_id: str) -> None:
    """Disable a persona."""
    self.require(persona_id).disable()

def active(self) -> Iterable[Persona]:
    """Return enabled personas."""
    return (
        persona
        for persona in self._personas.values()
        if persona.enabled
    )

def count(self) -> int:
    """Return the number of registered personas."""
    return len(self._personas)
```
