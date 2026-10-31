
import pytest

from waymark.disruptions.impact import analyze_disruption_impact
from waymark.schemas.disruption import Disruption
from waymark.schemas.plan import ProjectPlan
from waymark.schemas.task import Task


@pytest.fixture
def project_plan():
    return ProjectPlan(
        id="P1",
        name="Tech Fest",
        start_date="2026-12-01",
        deadline="2026-12-15",
        tasks=[
            Task(id="A", name="Venue Booking", duration_days=2),
            Task(id="B", name="Decoration", duration_days=2, dependencies=["A"]),
            Task(id="C", name="Stage Setup", duration_days=2, dependencies=["B"]),
            Task(id="D", name="Sound Setup", duration_days=1, dependencies=["A"]),
            Task(id="E", name="Final Inspection", duration_days=1, dependencies=["C", "D"]),
        ],
    )


def test_identifies_disrupted_and_downstream_tasks(project_plan):
    disruption = Disruption(
        task_id="B",
        delay_days=2,
        reason="Decoration team unavailable",
    )

    result = analyze_disruption_impact(project_plan, disruption)

    assert result == {"B", "C", "E"}


def test_does_not_include_independent_tasks(project_plan):
    disruption = Disruption(
        task_id="B",
        delay_days=2,
        reason="Decoration team unavailable",
    )

    result = analyze_disruption_impact(project_plan, disruption)

    assert "A" not in result
    assert "D" not in result


def test_raises_error_for_unknown_task(project_plan):
    disruption = Disruption(
        task_id="X",
        delay_days=2,
        reason="Unknown task",
    )

    with pytest.raises(ValueError, match="Unknown task ID: X"):
        analyze_disruption_impact(project_plan, disruption)
