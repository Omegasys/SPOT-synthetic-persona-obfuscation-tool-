import pytest

from spot.personas.manager import PersonaManager
from spot.personas.persona import Persona
from spot.personas.identity import Identity
from spot.personas.interests import Interests
from spot.personas.preferences import Preferences


def make_persona(persona_id):
    return Persona(
        id=persona_id,
        name=f"Persona {persona_id}",
        description="Integration-test synthetic persona",
        identity=Identity(
            age_range="25-34",
            location="US",
            language="en",
            attributes=["synthetic"],
        ),
        interests=Interests(
            primary=["technology"],
            secondary=["linux"],
        ),
        preferences=Preferences(
            content_types=["articles"],
            topics=["privacy"],
            languages=["en"],
        ),
        enabled=False,
        memory_enabled=True,
        synthetic_only=True,
    )


def test_persona_lifecycle():
    manager = PersonaManager()

    persona = make_persona("integration-persona")

    manager.add(persona)

    assert manager.get("integration-persona") is persona
    assert persona.enabled is False

    manager.enable("integration-persona")

    assert persona.enabled is True
    assert persona in manager.active()

    manager.disable("integration-persona")

    assert persona.enabled is False
    assert persona not in manager.active()

    manager.remove("integration-persona")

    with pytest.raises(KeyError):
        manager.require("integration-persona")


def test_multiple_personas_have_independent_lifecycles():
    manager = PersonaManager()

    first = make_persona("persona-a")
    second = make_persona("persona-b")

    manager.add(first)
    manager.add(second)

    manager.enable("persona-a")

    assert first.enabled is True
    assert second.enabled is False

    manager.enable("persona-b")

    assert first.enabled is True
    assert second.enabled is True

    manager.disable("persona-a")

    assert first.enabled is False
    assert second.enabled is True
