import pytest

from spot.personas.persona import Persona
from spot.personas.identity import Identity
from spot.personas.interests import Interests
from spot.personas.preferences import Preferences
from spot.personas.manager import PersonaManager
from spot.personas.demographics import Demographics
from spot.personas.routines import Routine, Routines
from spot.personas.memory import SyntheticMemory
from spot.personas.evolution import Evolution, EvolutionSettings


def make_persona(persona_id="test-persona"):
    return Persona(
        id=persona_id,
        name="Test Persona",
        description="Synthetic test persona",
        identity=Identity(
            age_range="25-34",
            location="US",
            language="en",
            attributes=["test"],
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


def test_persona_is_synthetic_only():
    persona = make_persona()

    assert persona.synthetic_only is True


def test_persona_starts_disabled():
    persona = make_persona()

    assert persona.enabled is False


def test_persona_enable():
    persona = make_persona()

    persona.enable()

    assert persona.enabled is True


def test_persona_disable():
    persona = make_persona()
    persona.enable()

    persona.disable()

    assert persona.enabled is False


def test_persona_serialization():
    persona = make_persona()

    data = persona.to_dict()

    assert data["id"] == "test-persona"
    assert data["name"] == "Test Persona"
    assert data["synthetic_only"] is True


def test_persona_round_trip():
    original = make_persona()

    restored = Persona.from_dict(original.to_dict())

    assert restored.id == original.id
    assert restored.name == original.name
    assert restored.synthetic_only == original.synthetic_only
    assert restored.interests.primary == original.interests.primary


def test_persona_manager_add_and_get():
    manager = PersonaManager()
    persona = make_persona()

    manager.add(persona)

    assert manager.get("test-persona") is persona


def test_persona_manager_require():
    manager = PersonaManager()
    persona = make_persona()

    manager.add(persona)

    assert manager.require("test-persona") is persona


def test_persona_manager_missing_persona():
    manager = PersonaManager()

    with pytest.raises(KeyError):
        manager.require("missing")


def test_persona_manager_enable_disable():
    manager = PersonaManager()
    persona = make_persona()

    manager.add(persona)

    manager.enable("test-persona")
    assert persona.enabled is True

    manager.disable("test-persona")
    assert persona.enabled is False


def test_interests():
    interests = Interests()

    interests.add_primary("linux")
    interests.add_secondary("hardware")

    assert interests.contains("linux")
    assert interests.contains("hardware")

    interests.remove("linux")

    assert not interests.contains("linux")


def test_demographics_round_trip():
    demographics = Demographics(
        age_range="25-34",
        location="US",
        language="en",
        attributes=["synthetic"],
    )

    restored = Demographics.from_dict(demographics.to_dict())

    assert restored.age_range == "25-34"
    assert restored.location == "US"
    assert restored.language == "en"


def test_routines():
    routines = Routines()

    routine = Routine(
        name="weekday",
        days=["monday", "tuesday"],
        start_hour=8,
        start_minute=0,
        end_hour=10,
        end_minute=0,
    )

    routines.add(routine)

    assert len(routines.for_day("monday")) == 1
    assert len(routines.for_day("sunday")) == 0


def test_synthetic_memory():
    memory = SyntheticMemory(max_entries=10)

    entry = memory.remember(
        topic="technology",
        content="Synthetic interest in Linux",
    )

    assert entry is not None
    assert len(memory.entries()) == 1

    results = memory.recall("technology")

    assert len(results) == 1


def test_memory_forget():
    memory = SyntheticMemory(max_entries=10)

    entry = memory.remember(
        topic="technology",
        content="Synthetic interest",
    )

    memory.forget(entry.id)

    assert len(memory.entries()) == 0


def test_evolution_is_bounded():
    evolution = Evolution(
        settings=EvolutionSettings(
            enabled=True,
            max_change_per_cycle=0.1,
        )
    )

    result = evolution.apply(
        traits={"exploration": 0.5},
    )

    assert 0.0 <= result["exploration"] <= 1.0
