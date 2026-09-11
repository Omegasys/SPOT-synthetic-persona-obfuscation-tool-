from spot.qubes.templates import (
    QubeTemplate,
    QubeTemplateManager,
)
from spot.qubes.disposable import (
    DisposableConfig,
    DisposableManager,
)


def test_qube_template_manager():
    manager = QubeTemplateManager()

    template = QubeTemplate(
        id="spot-test-template",
        name="SPOT Test Template",
        description="Synthetic test template",
    )

    manager.add(template)

    assert manager.get("spot-test-template") is template
    assert manager.require("spot-test-template") is template


def test_default_templates_exist():
    manager = QubeTemplateManager()

    available = manager.available()

    assert len(available) > 0


def test_disposable_qube_configuration():
    config = DisposableConfig(
        persistent=False,
        destroy_after_stop=True,
    )

    assert config.persistent is False
    assert config.destroy_after_stop is True


def test_disposable_manager_creates_isolated_qube():
    manager = DisposableManager()

    disposable = manager.create(
        "test-disposable",
        DisposableConfig(
            persistent=False,
            destroy_after_stop=True,
        ),
    )

    assert disposable.id == "test-disposable"
    assert disposable.config.persistent is False
    assert disposable.config.destroy_after_stop is True


def test_disposable_qube_is_not_persistent():
    manager = DisposableManager()

    disposable = manager.create(
        "temporary-persona",
        DisposableConfig(
            persistent=False,
            destroy_after_stop=True,
        ),
    )

    assert disposable.config.persistent is False
