from datetime import date

import pytest

from waymark.scheduling.replanner import replan_schedule
from waymark.schemas.disruption import Disruption
from waymark.schemas.plan import ProjectPlan
from waymark.schemas.schedule import Schedule, ScheduledTask
from waymark.schemas.task import Task


@pytest.fixture
def project_plan():
    return ProjectPlan(
        id="P1",
        name="Tech Fest",
        start_date="2026-12-01",
        deadline="2026-12-15",
        tasks=[
            Task(
                id="A",
                name="Venue Booking",
                duration_days=2,
            ),
            Task(
                id="B",
                name="Decoration",
                duration_days=2,
                dependencies=["A"],
            ),
            Task(
                id="C",
                name="Stage Setup",
                duration_days=2,
                dependencies=["B"],
            ),
            Task(
                id="D",
                name="Sound Setup",
                duration_days=1,
                dependencies=["A"],
            ),
            Task(
                id="E",
                name="Final Inspection",
                duration_days=1,
                dependencies=["C", "D"],
            ),
        ],
    )


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
            ScheduledTask(
                task_id="D",
                start_date=date(2026, 12, 3),
                finish_date=date(2026, 12, 4),
            ),
            ScheduledTask(
                task_id="E",
                start_date=date(2026, 12, 7),
                finish_date=date(2026, 12, 8),
            ),
        ]
    )


@pytest.fixture
def disruption():
    return Disruption(
        task_id="B",
        delay_days=2,
        reason="Decoration team unavailable",
    )


def test_replans_disrupted_task(
    project_plan,
    original_schedule,
    disruption,
):
    revised = replan_schedule(
        project_plan,
        original_schedule,
        disruption,
    )

    task_b = next(task for task in revised.tasks if task.task_id == "B")

    assert task_b.start_date == date(2026, 12, 5)
    assert task_b.finish_date == date(2026, 12, 7)


def test_replans_downstream_tasks(
    project_plan,
    original_schedule,
    disruption,
):
    revised = replan_schedule(
        project_plan,
        original_schedule,
        disruption,
    )

    tasks = {task.task_id: task for task in revised.tasks}

    assert tasks["C"].start_date == date(2026, 12, 7)
    assert tasks["C"].finish_date == date(2026, 12, 9)

    assert tasks["E"].start_date == date(2026, 12, 9)
    assert tasks["E"].finish_date == date(2026, 12, 10)


def test_preserves_unaffected_tasks(
    project_plan,
    original_schedule,
    disruption,
):
    revised = replan_schedule(
        project_plan,
        original_schedule,
        disruption,
    )

    tasks = {task.task_id: task for task in revised.tasks}
    original = {task.task_id: task for task in original_schedule.tasks}

    assert tasks["A"] == original["A"]
    assert tasks["D"] == original["D"]


def test_respects_all_dependencies(
    project_plan,
    original_schedule,
    disruption,
):
    revised = replan_schedule(
        project_plan,
        original_schedule,
        disruption,
    )

    tasks = {task.task_id: task for task in revised.tasks}

    assert tasks["B"].start_date >= tasks["A"].finish_date
    assert tasks["C"].start_date >= tasks["B"].finish_date
    assert tasks["E"].start_date >= tasks["C"].finish_date
    assert tasks["E"].start_date >= tasks["D"].finish_date


def test_rejects_incomplete_original_schedule(
    project_plan,
    original_schedule,
    disruption,
):
    incomplete_schedule = Schedule(
        tasks=[task for task in original_schedule.tasks if task.task_id != "E"]
    )

    with pytest.raises(
        ValueError,
        match="Original schedule is missing tasks: E",
    ):
        replan_schedule(
            project_plan,
            incomplete_schedule,
            disruption,
        )


def test_rejects_unexpected_tasks(
    project_plan,
    original_schedule,
    disruption,
):
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
        match="Original schedule contains unknown tasks: X",
    ):
        replan_schedule(
            project_plan,
            unexpected_schedule,
            disruption,
        )
