"""SPOT synthetic persona generator."""

from **future** import annotations

import random
import uuid
from typing import Iterable, List

from .demographics import Demographics
from .interests import Interests
from .persona import Persona
from .preferences import Preferences

class PersonaGenerator:
"""Generate synthetic personas from controlled components."""

```
DEFAULT_NAMES = [
    "Alex",
    "Morgan",
    "Jordan",
    "Taylor",
    "Riley",
    "Casey",
    "Jamie",
    "Avery",
]

def __init__(
    self,
    seed: int | None = None,
) -> None:
    self.random = random.Random(seed)

def generate(
    self,
    name: str | None = None,
    interests: Iterable[str] | None = None,
) -> Persona:
    """Generate a basic synthetic persona."""
    persona_name = (
        name
        if name is not None
        else self.random.choice(self.DEFAULT_NAMES)
    )

    persona_id = self._generate_id(persona_name)

    selected_interests = list(interests or [])

    persona = Persona(
        id=persona_id,
        name=persona_name,
        description=(
            "Automatically generated synthetic persona."
        ),
        identity=self._generate_identity(),
        interests=Interests(
            primary=selected_interests
        ),
        preferences=Preferences(),
        enabled=False,
        memory_enabled=True,
        synthetic_only=True,
    )

    return persona

def generate_from_template(
    self,
    template: dict,
) -> Persona:
    """Create a persona from template data."""
    data = dict(template)

    if "id" not in data:
        name = str(
            data.get(
                "name",
                self.random.choice(self.DEFAULT_NAMES),
            )
        )
        data["id"] = self._generate_id(name)

    return Persona.from_dict(data)

def _generate_identity(self) -> Demographics:
    """Generate synthetic demographic defaults."""
    age_ranges = [
        "18-24",
        "25-34",
        "35-44",
        "45-54",
    ]

    return Demographics(
        age_range=self.random.choice(age_ranges),
        location="synthetic",
        language="en",
    )

@staticmethod
def _generate_id(name: str) -> str:
    """Generate a unique persona identifier."""
    normalized = (
        name.lower()
        .replace(" ", "-")
    )

    suffix = uuid.uuid4().hex[:8]

    return f"{normalized}-{suffix}"
```
