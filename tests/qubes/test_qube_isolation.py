from spot.qubes.disposable import (
    DisposableConfig,
    DisposableManager,
)
from spot.qubes.persona_qubes import (
    PersonaQube,
    PersonaQubeManager,
)


def test_disposable_qube_cannot_be_persistent():
    config = DisposableConfig(
        persistent=False,
        destroy_after_stop=True,
    )

    assert config.persistent is False


def test_persona_qube_mapping():
    manager = PersonaQubeManager()

    mapping = PersonaQube(
        persona_id="persona-a",
        qube_name="spot-persona-a",
        disposable=False,
        enabled=True,
    )

    manager.assign(mapping)

    result = manager.get("persona-a")

    assert result is mapping
    assert result.qube_name == "spot-persona-a"


def test_persona_mapping_is_unique():
    manager = PersonaQubeManager()

    first = PersonaQube(
        persona_id="persona-a",
        qube_name="spot-persona-a",
        disposable=False,
        enabled=True,
    )

    manager.assign(first)

    assert manager.qube_for("persona-a") == "spot-persona-a"
    assert manager.persona_for("spot-persona-a") == "persona-a"


def test_persona_can_be_disabled():
    manager = PersonaQubeManager()

    mapping = PersonaQube(
        persona_id="persona-a",
        qube_name="spot-persona-a",
        disposable=False,
        enabled=True,
    )

    manager.assign(mapping)
    manager.disable("persona-a")

    assert mapping.enabled is False


def test_disposable_and_persistent_flags_are_not_both_enabled():
    manager = PersonaQubeManager()

    mapping = PersonaQube(
        persona_id="persona-a",
        qube_name="spot-persona-a",
        disposable=True,
        enabled=True,
    )

    assert not (
        mapping.disposable and getattr(mapping, "persistent", False)
    )
