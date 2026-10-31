from datetime import date

import pytest
from pydantic import ValidationError

from waymark.scheduling.comparison import compare_schedules
from waymark.schemas.schedule import Schedule, ScheduledTask
from waymark.schemas.schedule_comparison import ScheduleComparison, TaskScheduleChange


@pytest.fixture
def original_schedule():
    return Schedule(
        tasks=[
            ScheduledTask(
                task_id="A",
                start_date=date(2026, 12, 1),
                finish_date=date(2026, 12, 3),
            ),
            ScheduledTask(
                task_id="B",
                start_date=date(2026, 12, 3),
                finish_date=date(2026, 12, 5),
            ),
            ScheduledTask(
                task_id="C",
                start_date=date(2026, 12, 5),
                finish_date=date(2026, 12, 7),
            ),
        ]
    )


@pytest.fixture
def revised_schedule():
    return Schedule(
        tasks=[
            ScheduledTask(
                task_id="A",
                start_date=date(2026, 12, 1),
                finish_date=date(2026, 12, 3),
            ),
            ScheduledTask(
                task_id="B",
                start_date=date(2026, 12, 5),
                finish_date=date(2026, 12, 7),
            ),
            ScheduledTask(
                task_id="C",
                start_date=date(2026, 12, 7),
                finish_date=date(2026, 12, 9),
            ),
        ]
    )


def test_creates_valid_task_schedule_change():
    change = TaskScheduleChange(
        task_id="B",
        original_start=date(2026, 12, 3),
        original_finish=date(2026, 12, 5),
        revised_start=date(2026, 12, 5),
        revised_finish=date(2026, 12, 7),
        delay_days=2,
    )

    assert change.task_id == "B"
    assert change.delay_days == 2


def test_rejects_empty_task_id():
    with pytest.raises(ValidationError):
        TaskScheduleChange(
            task_id="",
            original_start=date(2026, 12, 3),
            original_finish=date(2026, 12, 5),
            revised_start=date(2026, 12, 5),
            revised_finish=date(2026, 12, 7),
            delay_days=2,
        )


def test_creates_valid_schedule_comparison():
    change = TaskScheduleChange(
        task_id="B",
        original_start=date(2026, 12, 3),
        original_finish=date(2026, 12, 5),
        revised_start=date(2026, 12, 5),
        revised_finish=date(2026, 12, 7),
        delay_days=2,
    )

    comparison = ScheduleComparison(changes=[change])

    assert len(comparison.changes) == 1
    assert comparison.changes[0].task_id == "B"


def test_rejects_extra_fields():
    with pytest.raises(ValidationError):
        TaskScheduleChange(
            task_id="B",
            original_start=date(2026, 12, 3),
            original_finish=date(2026, 12, 5),
            revised_start=date(2026, 12, 5),
            revised_finish=date(2026, 12, 7),
            delay_days=2,
            unexpected_field="invalid",
        )


def test_calculates_task_delays(original_schedule, revised_schedule):
    comparison = compare_schedules(original_schedule, revised_schedule)

    delays = {change.task_id: change.delay_days for change in comparison.changes}

    assert delays == {
        "A": 0,
        "B": 2,
        "C": 2,
    }


def test_preserves_unchanged_task_dates(original_schedule, revised_schedule):
    comparison = compare_schedules(original_schedule, revised_schedule)

    change_a = next(change for change in comparison.changes if change.task_id == "A")

    assert change_a.original_start == change_a.revised_start
    assert change_a.original_finish == change_a.revised_finish
    assert change_a.delay_days == 0


def test_detects_tasks_moved_earlier(original_schedule):
    earlier_schedule = Schedule(
        tasks=[
            ScheduledTask(
                task_id="A",
                start_date=date(2026, 11, 30),
                finish_date=date(2026, 12, 2),
            ),
            *original_schedule.tasks[1:],
        ]
    )

    comparison = compare_schedules(original_schedule, earlier_schedule)

    change_a = next(change for change in comparison.changes if change.task_id == "A")

    assert change_a.delay_days == -1


def test_rejects_missing_tasks(original_schedule):
    incomplete_schedule = Schedule(tasks=original_schedule.tasks[:2])

    with pytest.raises(
        ValueError,
        match="Original and revised schedules must contain the same tasks",
    ):
        compare_schedules(original_schedule, incomplete_schedule)


def test_rejects_unexpected_tasks(original_schedule):
    unexpected_schedule = Schedule(
        tasks=[
            *original_schedule.tasks,
            ScheduledTask(
                task_id="X",
                start_date=date(2026, 12, 1),
                finish_date=date(2026, 12, 2),
            ),
        ]
    )

    with pytest.raises(
        ValueError,
        match="Original and revised schedules must contain the same tasks",
    ):
        compare_schedules(original_schedule, unexpected_schedule)
