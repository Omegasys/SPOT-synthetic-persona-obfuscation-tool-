from datetime import datetime, timedelta, timezone

from spot.scheduler.timers import TimerManager
from spot.scheduler.calendar import CalendarRule, ScheduleCalendar
from spot.scheduler.randomizer import ScheduleRandomizer
from spot.scheduler.concurrency import (
    ConcurrencyController,
    ConcurrencyPolicy,
)


def test_timer_manager_create_and_get():
    manager = TimerManager()

    timer = manager.create(
        timer_id="test-timer",
        interval_seconds=60,
    )

    assert manager.get("test-timer") is timer


def test_calendar_matches_day():
    calendar = ScheduleCalendar()

    rule = CalendarRule(
        days=["monday"],
        preferred_hour=10,
        preferred_minute=0,
    )

    monday = datetime(
        2026,
        9,
        7,
        10,
        0,
        tzinfo=timezone.utc,
    )

    assert calendar.matches(rule, monday) is True


def test_calendar_rejects_wrong_day():
    calendar = ScheduleCalendar()

    rule = CalendarRule(
        days=["monday"],
        preferred_hour=10,
        preferred_minute=0,
    )

    tuesday = datetime(
        2026,
        9,
        8,
        10,
        0,
        tzinfo=timezone.utc,
    )

    assert calendar.matches(rule, tuesday) is False


def test_schedule_randomizer_stays_near_original():
    randomizer = ScheduleRandomizer()

    original = datetime(
        2026,
        9,
        10,
        12,
        0,
        tzinfo=timezone.utc,
    )

    result = randomizer.adjust_datetime(
        original,
        max_delay_seconds=300,
    )

    difference = abs((result - original).total_seconds())

    assert difference <= 300


def test_concurrency_limit():
    controller = ConcurrencyController(
        ConcurrencyPolicy(
            max_concurrent=2,
            max_per_persona=1,
        )
    )

    assert controller.can_start("persona-a") is True

    controller.start("persona-a")

    assert controller.can_start("persona-a") is False
    assert controller.can_start("persona-b") is True


def test_concurrency_finish():
    controller = ConcurrencyController(
        ConcurrencyPolicy(
            max_concurrent=2,
            max_per_persona=1,
        )
    )

    controller.start("persona-a")
    controller.finish("persona-a")

    assert controller.can_start("persona-a") is True
    assert controller.available_slots() == 2
