from datetime import date

import pytest
from pydantic import ValidationError

from waymark.schemas.schedule import Schedule, ScheduledTask


def test_scheduled_task_accepts_valid_data():
    task = ScheduledTask(
        task_id="book_venue",
        start_date=date(2026, 11, 1),
        finish_date=date(2026, 11, 3),
    )

    assert task.task_id == "book_venue"
    assert task.start_date == date(2026, 11, 1)
    assert task.finish_date == date(2026, 11, 3)


def test_scheduled_task_rejects_blank_task_id():
    with pytest.raises(ValidationError):
        ScheduledTask(
            task_id="   ",
            start_date=date(2026, 11, 1),
            finish_date=date(2026, 11, 3),
        )


def test_scheduled_task_rejects_finish_date_before_start_date():
    with pytest.raises(ValidationError, match="Finish date must be after"):
        ScheduledTask(
            task_id="book_venue",
            start_date=date(2026, 11, 3),
            finish_date=date(2026, 11, 1),
        )


def test_scheduled_task_rejects_finish_date_equal_to_start_date():
    with pytest.raises(ValidationError, match="Finish date must be after"):
        ScheduledTask(
            task_id="book_venue",
            start_date=date(2026, 11, 1),
            finish_date=date(2026, 11, 1),
        )


def test_schedule_accepts_valid_tasks():
    schedule = Schedule(
        tasks=[
            ScheduledTask(
                task_id="book_venue",
                start_date=date(2026, 11, 1),
                finish_date=date(2026, 11, 3),
            ),
            ScheduledTask(
                task_id="publish_schedule",
                start_date=date(2026, 11, 3),
                finish_date=date(2026, 11, 4),
            ),
        ]
    )

    assert len(schedule.tasks) == 2


def test_schedule_rejects_empty_task_list():
    with pytest.raises(ValidationError):
        Schedule(tasks=[])


def test_schedule_rejects_duplicate_task_ids():
    with pytest.raises(
        ValidationError,
        match="Scheduled task IDs must be unique",
    ):
        Schedule(
            tasks=[
                ScheduledTask(
                    task_id="book_venue",
                    start_date=date(2026, 11, 1),
                    finish_date=date(2026, 11, 3),
                ),
                ScheduledTask(
                    task_id="book_venue",
                    start_date=date(2026, 11, 3),
                    finish_date=date(2026, 11, 4),
                ),
            ]
        )


def test_scheduled_task_rejects_unexpected_fields():
    with pytest.raises(ValidationError):
        ScheduledTask(
            task_id="book_venue",
            start_date=date(2026, 11, 1),
            finish_date=date(2026, 11, 3),
            duration_days=2,
        )
