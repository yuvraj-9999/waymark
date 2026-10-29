from datetime import date

import pytest
from pydantic import ValidationError

from waymark.schemas.plan import ProjectPlan
from waymark.schemas.task import Task


def test_plan_rejects_empty_task_list():
    with pytest.raises(ValidationError):
        ProjectPlan(
            id="tech_fest",
            name="College Tech Fest",
            start_date=date(2026, 11, 1),
            deadline=date(2026, 11, 10),
            tasks=[],
        )


def test_plan_rejects_deadline_before_start_date():
    with pytest.raises(ValidationError, match="Deadline cannot precede"):
        ProjectPlan(
            id="tech_fest",
            name="College Tech Fest",
            start_date=date(2026, 11, 10),
            deadline=date(2026, 11, 1),
            tasks=[
                Task(
                    id="venue",
                    name="Book venue",
                    duration_days=1,
                )
            ],
        )


def test_plan_rejects_duplicate_task_ids():
    with pytest.raises(ValidationError, match="unique"):
        ProjectPlan(
            id="tech_fest",
            name="College Tech Fest",
            start_date=date(2026, 11, 1),
            deadline=date(2026, 11, 10),
            tasks=[
                Task(id="venue", name="Book venue", duration_days=1),
                Task(id="venue", name="Confirm venue", duration_days=2),
            ],
        )


def test_plan_rejects_unknown_dependency():
    with pytest.raises(ValidationError, match="unknown dependencies"):
        ProjectPlan(
            id="tech_fest",
            name="College Tech Fest",
            start_date=date(2026, 11, 1),
            deadline=date(2026, 11, 10),
            tasks=[
                Task(
                    id="publish",
                    name="Publish schedule",
                    duration_days=1,
                    dependencies=["confirm_speakers"],
                )
            ],
        )


def test_plan_accepts_valid_dependency():
    plan = ProjectPlan(
        id="tech_fest",
        name="College Tech Fest",
        start_date=date(2026, 11, 1),
        deadline=date(2026, 11, 10),
        tasks=[
            Task(id="venue", name="Book venue", duration_days=1),
            Task(
                id="publish",
                name="Publish schedule",
                duration_days=1,
                dependencies=["venue"],
            ),
        ],
    )

    assert len(plan.tasks) == 2
    assert plan.tasks[1].dependencies == ["venue"]


def test_plan_rejects_blank_id():
    with pytest.raises(ValidationError):
        ProjectPlan(
            id=" ",
            name="College Tech Fest",
            start_date=date(2026, 11, 1),
            deadline=date(2026, 11, 10),
            tasks=[Task(id="venue", name="Book venue", duration_days=1)],
        )


def test_plan_rejects_blank_name():
    with pytest.raises(ValidationError):
        ProjectPlan(
            id="tech_fest",
            name="   ",
            start_date=date(2026, 11, 1),
            deadline=date(2026, 11, 10),
            tasks=[Task(id="venue", name="Book venue", duration_days=1)],
        )
