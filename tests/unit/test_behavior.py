from spot.behavior.model import BehaviorModel, BehaviorTraits
from spot.behavior.context import BehaviorContext
from spot.behavior.decision import DecisionEngine
from spot.behavior.consistency import ConsistencyController
from spot.behavior.noise_budget import NoiseBudget, NoiseBudgetSettings
from spot.behavior.randomization import Randomization


def test_behavior_traits_are_bounded():
    traits = BehaviorTraits(
        activity_level=0.5,
        exploration=0.6,
        consistency=0.7,
        randomness=0.4,
        research_depth=0.5,
        session_length=0.5,
        topic_switching=0.3,
    )

    assert 0.0 <= traits.activity_level <= 1.0
    assert 0.0 <= traits.exploration <= 1.0
    assert 0.0 <= traits.consistency <= 1.0
    assert 0.0 <= traits.randomness <= 1.0


def test_behavior_model_can_be_created():
    model = BehaviorModel(
        traits=BehaviorTraits(),
        preferred_actions=["search", "browsing"],
    )

    assert "search" in model.preferred_actions
    assert "browsing" in model.preferred_actions


def test_behavior_context_with_action():
    context = BehaviorContext(
        persona_id="test",
        session_id="session",
    )

    updated = context.with_action("search")

    assert updated.previous_action == "search"


def test_decision_engine_returns_candidate():
    model = BehaviorModel(
        traits=BehaviorTraits(),
        preferred_actions=["search", "browsing"],
    )

    engine = DecisionEngine(model)

    context = BehaviorContext(
        persona_id="test",
        session_id="session",
    )

    decision = engine.decide(
        context=context,
        candidates=["search", "browsing"],
    )

    assert decision.action in {"search", "browsing"}


def test_consistency_controller_records_actions():
    controller = ConsistencyController()

    controller.record("search")
    controller.record("search")
    controller.record("browsing")

    assert controller.recent_actions() == [
        "search",
        "search",
        "browsing",
    ]


def test_consistency_controller_counts_repeated_actions():
    controller = ConsistencyController()

    controller.record("search")
    controller.record("search")
    controller.record("search")

    assert controller.repeated_action_count("search") == 3


def test_noise_budget():
    budget = NoiseBudget(
        NoiseBudgetSettings(
            max_randomized_decisions=2,
        )
    )

    assert budget.allow() is True
    budget.consume()

    assert budget.allow() is True
    budget.consume()

    assert budget.allow() is False
    assert budget.exhausted() is True


def test_randomization_stays_bounded():
    randomization = Randomization()

    value = randomization.bounded_variation(
        value=0.5,
        variation=0.1,
    )

    assert 0.0 <= value <= 1.0
