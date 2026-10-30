from datetime import date

from waymark.scheduling.scheduler import calculate_schedule
from waymark.schemas.plan import ProjectPlan
from waymark.schemas.task import Task


def test_independent_tasks_start_on_project_start_date():
    plan = ProjectPlan(
        id="project-1",
        name="Test Project",
        start_date=date(2026, 11, 1),
        deadline=date(2026, 11, 10),
        tasks=[
            Task(
                id="A",
                name="Task A",
                duration_days=2,
            ),
            Task(
                id="B",
                name="Task B",
                duration_days=3,
            ),
        ],
    )

    schedule = calculate_schedule(plan)

    scheduled_tasks = {task.task_id: task for task in schedule.tasks}

    assert scheduled_tasks["A"].start_date == date(2026, 11, 1)
    assert scheduled_tasks["A"].finish_date == date(2026, 11, 3)

    assert scheduled_tasks["B"].start_date == date(2026, 11, 1)
    assert scheduled_tasks["B"].finish_date == date(2026, 11, 4)


def test_dependent_task_starts_after_dependency_finishes():
    plan = ProjectPlan(
        id="project-2",
        name="Dependent Tasks Project",
        start_date=date(2026, 11, 1),
        deadline=date(2026, 11, 10),
        tasks=[
            Task(
                id="A",
                name="Design",
                duration_days=2,
            ),
            Task(
                id="B",
                name="Development",
                duration_days=3,
                dependencies=["A"],
            ),
        ],
    )

    schedule = calculate_schedule(plan)

    scheduled_tasks = {task.task_id: task for task in schedule.tasks}

    assert scheduled_tasks["A"].start_date == date(2026, 11, 1)
    assert scheduled_tasks["A"].finish_date == date(2026, 11, 3)

    assert scheduled_tasks["B"].start_date == date(2026, 11, 3)
    assert scheduled_tasks["B"].finish_date == date(2026, 11, 6)


def test_multiple_dependencies_use_latest_finish_date():
    plan = ProjectPlan(
        id="project-3",
        name="Multiple Dependencies Project",
        start_date=date(2026, 11, 1),
        deadline=date(2026, 11, 15),
        tasks=[
            Task(
                id="A",
                name="Initial Task",
                duration_days=2,
            ),
            Task(
                id="B",
                name="Task B",
                duration_days=4,
                dependencies=["A"],
            ),
            Task(
                id="C",
                name="Task C",
                duration_days=3,
                dependencies=["A"],
            ),
            Task(
                id="D",
                name="Final Task",
                duration_days=2,
                dependencies=["B", "C"],
            ),
        ],
    )

    schedule = calculate_schedule(plan)

    scheduled_tasks = {task.task_id: task for task in schedule.tasks}

    assert scheduled_tasks["D"].start_date == date(2026, 11, 7)
    assert scheduled_tasks["D"].finish_date == date(2026, 11, 9)


import pytest


def test_circular_dependencies_raise_value_error():
    plan = ProjectPlan(
        id="project-4",
        name="Circular Dependencies Project",
        start_date=date(2026, 11, 1),
        deadline=date(2026, 11, 10),
        tasks=[
            Task(
                id="A",
                name="Task A",
                duration_days=2,
                dependencies=["B"],
            ),
            Task(
                id="B",
                name="Task B",
                duration_days=3,
                dependencies=["A"],
            ),
        ],
    )

    with pytest.raises(
        ValueError,
        match="Cannot schedule a project with circular dependencies.",
    ):
        calculate_schedule(plan)
