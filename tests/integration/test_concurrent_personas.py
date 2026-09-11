from spot.personas.manager import PersonaManager
from spot.personas.persona import Persona
from spot.personas.identity import Identity
from spot.personas.interests import Interests
from spot.personas.preferences import Preferences
from spot.scheduler.concurrency import (
    ConcurrencyController,
    ConcurrencyPolicy,
)


def make_persona(persona_id):
    return Persona(
        id=persona_id,
        name=persona_id,
        description="Synthetic integration persona",
        identity=Identity(
            age_range="25-34",
            location="US",
            language="en",
            attributes=["synthetic"],
        ),
        interests=Interests(),
        preferences=Preferences(),
        synthetic_only=True,
    )


def test_concurrent_personas_respect_global_limit():
    personas = PersonaManager()

    for persona_id in ("one", "two", "three"):
        personas.add(make_persona(persona_id))

    controller = ConcurrencyController(
        ConcurrencyPolicy(
            max_concurrent=2,
            max_per_persona=1,
        )
    )

    controller.start("one")
    controller.start("two")

    assert controller.can_start("one") is False
    assert controller.can_start("two") is False
    assert controller.can_start("three") is False
    assert controller.available_slots() == 0


def test_persona_cannot_run_twice():
    controller = ConcurrencyController(
        ConcurrencyPolicy(
            max_concurrent=3,
            max_per_persona=1,
        )
    )

    assert controller.can_start("persona-a") is True

    controller.start("persona-a")

    assert controller.can_start("persona-a") is False
    assert controller.available_slots() == 2


def test_persona_slot_is_released_after_finish():
    controller = ConcurrencyController(
        ConcurrencyPolicy(
            max_concurrent=2,
            max_per_persona=1,
        )
    )

    controller.start("persona-a")
    controller.start("persona-b")

    assert controller.available_slots() == 0

    controller.finish("persona-a")

    assert controller.available_slots() == 1
    assert controller.can_start("persona-a") is True


def test_personas_can_run_independently():
    controller = ConcurrencyController(
        ConcurrencyPolicy(
            max_concurrent=3,
            max_per_persona=1,
        )
    )

    controller.start("persona-a")

    assert controller.can_start("persona-a") is False
    assert controller.can_start("persona-b") is True
    assert controller.can_start("persona-c") is True
