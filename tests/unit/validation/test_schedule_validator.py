from datetime import date

from waymark.schemas.plan import ProjectPlan
from waymark.schemas.schedule import Schedule, ScheduledTask
from waymark.schemas.task import Task
from waymark.validation.schedule_validator import validate_schedule


def test_valid_task_coverage_returns_no_errors():
    plan = ProjectPlan(
        id="project-1",
        name="Test Project",
        start_date=date(2026, 11, 1),
        deadline=date(2026, 11, 10),
        tasks=[
            Task(id="A", name="Task A", duration_days=2),
            Task(id="B", name="Task B", duration_days=3),
        ],
    )

    schedule = Schedule(
        tasks=[
            ScheduledTask(
                task_id="A",
                start_date=date(2026, 11, 1),
                finish_date=date(2026, 11, 3),
            ),
            ScheduledTask(
                task_id="B",
                start_date=date(2026, 11, 3),
                finish_date=date(2026, 11, 6),
            ),
        ],
    )

    errors = validate_schedule(plan, schedule)

    assert errors == []


def test_missing_task_is_reported():
    plan = ProjectPlan(
        id="project-2",
        name="Test Project",
        start_date=date(2026, 11, 1),
        deadline=date(2026, 11, 10),
        tasks=[
            Task(id="A", name="Task A", duration_days=2),
            Task(id="B", name="Task B", duration_days=3),
        ],
    )

    schedule = Schedule(
        tasks=[
            ScheduledTask(
                task_id="A",
                start_date=date(2026, 11, 1),
                finish_date=date(2026, 11, 3),
            ),
        ],
    )

    errors = validate_schedule(plan, schedule)

    assert errors == ["Task 'B' is missing from the schedule."]


def test_unexpected_task_is_reported():
    plan = ProjectPlan(
        id="project-3",
        name="Test Project",
        start_date=date(2026, 11, 1),
        deadline=date(2026, 11, 10),
        tasks=[
            Task(id="A", name="Task A", duration_days=2),
            Task(id="B", name="Task B", duration_days=3),
        ],
    )

    schedule = Schedule(
        tasks=[
            ScheduledTask(
                task_id="A",
                start_date=date(2026, 11, 1),
                finish_date=date(2026, 11, 3),
            ),
            ScheduledTask(
                task_id="B",
                start_date=date(2026, 11, 3),
                finish_date=date(2026, 11, 6),
            ),
            ScheduledTask(
                task_id="C",
                start_date=date(2026, 11, 6),
                finish_date=date(2026, 11, 8),
            ),
        ],
    )

    errors = validate_schedule(plan, schedule)

    assert errors == ["Task 'C' is not part of the project plan."]


def test_task_starting_before_project_start_is_reported():
    plan = ProjectPlan(
        id="project-4",
        name="Test Project",
        start_date=date(2026, 11, 1),
        deadline=date(2026, 11, 10),
        tasks=[
            Task(id="A", name="Task A", duration_days=2),
        ],
    )

    schedule = Schedule(
        tasks=[
            ScheduledTask(
                task_id="A",
                start_date=date(2026, 10, 30),
                finish_date=date(2026, 11, 2),
            ),
        ],
    )

    errors = validate_schedule(plan, schedule)

    assert errors == ["Task 'A' starts before the project start date."]


def test_task_finishing_after_project_deadline_is_reported():
    plan = ProjectPlan(
        id="project-5",
        name="Test Project",
        start_date=date(2026, 11, 1),
        deadline=date(2026, 11, 10),
        tasks=[
            Task(id="A", name="Task A", duration_days=3),
        ],
    )

    schedule = Schedule(
        tasks=[
            ScheduledTask(
                task_id="A",
                start_date=date(2026, 11, 8),
                finish_date=date(2026, 11, 11),
            ),
        ],
    )

    errors = validate_schedule(plan, schedule)

    assert errors == ["Task 'A' finishes after the project deadline."]


def test_task_starting_before_dependency_finishes_is_reported():
    plan = ProjectPlan(
        id="project-6",
        name="Test Project",
        start_date=date(2026, 11, 1),
        deadline=date(2026, 11, 10),
        tasks=[
            Task(id="A", name="Task A", duration_days=2),
            Task(
                id="B",
                name="Task B",
                duration_days=3,
                dependencies=["A"],
            ),
        ],
    )

    schedule = Schedule(
        tasks=[
            ScheduledTask(
                task_id="A",
                start_date=date(2026, 11, 1),
                finish_date=date(2026, 11, 3),
            ),
            ScheduledTask(
                task_id="B",
                start_date=date(2026, 11, 2),
                finish_date=date(2026, 11, 5),
            ),
        ],
    )

    errors = validate_schedule(plan, schedule)

    assert errors == ["Task 'B' starts before dependency 'A' finishes."]


def test_task_finishing_exactly_on_deadline_is_valid():
    plan = ProjectPlan(
        id="project-7",
        name="Test Project",
        start_date=date(2026, 11, 1),
        deadline=date(2026, 11, 10),
        tasks=[
            Task(id="A", name="Task A", duration_days=2),
        ],
    )

    schedule = Schedule(
        tasks=[
            ScheduledTask(
                task_id="A",
                start_date=date(2026, 11, 8),
                finish_date=date(2026, 11, 10),
            ),
        ],
    )

    errors = validate_schedule(plan, schedule)

    assert errors == []
