from spot.core.engine import Engine
from spot.core.controller import Controller
from spot.safety.emergency_stop import EmergencyStop


def test_emergency_stop_blocks_activity():
    emergency_stop = EmergencyStop()

    assert emergency_stop.allows_activity() is True

    emergency_stop.activate()

    assert emergency_stop.allows_activity() is False


def test_emergency_stop_requires_reset():
    emergency_stop = EmergencyStop()

    emergency_stop.activate()

    assert emergency_stop.allows_activity() is False

    emergency_stop.reset()

    assert emergency_stop.allows_activity() is True


def test_engine_emergency_stop_changes_state():
    engine = Engine()

    engine.start()
    engine.emergency_stop()

    assert engine.state.emergency_stop is True


def test_controller_emergency_stop():
    controller = Controller()

    controller.emergency_stop()

    assert controller.state.emergency_stop is True


def test_emergency_stop_is_fail_closed():
    emergency_stop = EmergencyStop()

    emergency_stop.activate()

    assert emergency_stop.allows_activity() is False

    emergency_stop.request_reset()

    assert emergency_stop.allows_activity() is False
