from datetime import date

from waymark.orchestration import nodes
from waymark.orchestration.graph import waymark_graph
from waymark.schemas.disruption import Disruption
from waymark.schemas.execution import (
    ExecutionPlan,
    ExecutionStep,
    StakeholderCommunication,
)
from waymark.schemas.plan import ProjectPlan
from waymark.schemas.recovery import RecoveryPlan, RecoveryStrategy
from waymark.schemas.resource_scout import ResourceScoutResult
from waymark.schemas.review import RecoveryReview, StrategyReview
from waymark.schemas.schedule import Schedule, ScheduledTask
from waymark.schemas.task import Task


def test_complete_orchestration_workflow(monkeypatch):
    # Arrange: create a project with task dependencies.
    plan = ProjectPlan(
        id="project-1",
        name="Event Preparation",
        start_date=date(2026, 12, 1),
        deadline=date(2026, 12, 20),
        tasks=[
            Task(id="A", name="Venue Booking", duration_days=2, dependencies=[]),
            Task(id="B", name="Decoration", duration_days=2, dependencies=["A"]),
            Task(id="C", name="Stage Setup", duration_days=2, dependencies=["B"]),
            Task(id="D", name="Sound Setup", duration_days=1, dependencies=["A"]),
            Task(
                id="E",
                name="Final Inspection",
                duration_days=1,
                dependencies=["C", "D"],
            ),
        ],
    )

    original_schedule = Schedule(
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

    disruption = Disruption(
        task_id="B",
        delay_days=2,
        reason="Decoration materials are delayed.",
    )

    resource_result = ResourceScoutResult(
        search_performed=False,
        search_query="",
        explanation="No alternative resource search needed.",
        candidates=[],
    )

    recovery_plan = RecoveryPlan(
        strategies=[
            RecoveryStrategy(
                name="Reorganize preparation",
                description="Adjust preparation activities around the delay.",
                affected_tasks=["B", "C", "E"],
                benefits=["Keeps the project organized"],
                risks=["Requires coordination"],
                assumptions=["Task durations remain unchanged"],
            )
        ],
        recommendation="Use the revised schedule and coordinate affected tasks.",
    )

    recovery_review = RecoveryReview(
        strategy_reviews=[
            StrategyReview(
                strategy_name="Reorganize preparation",
                is_acceptable=True,
                issues=[],
                suggestions=[],
                severity="none",
            )
        ],
        overall_assessment="The proposed recovery strategy is acceptable.",
        approved=True,
    )

    execution_plan = ExecutionPlan(
        action_steps=[
            ExecutionStep(
                step=1,
                description="Coordinate the revised decoration schedule.",
                related_tasks=["B", "C"],
                priority="high",
            ),
            ExecutionStep(
                step=2,
                description="Confirm final inspection timing.",
                related_tasks=["E"],
                priority="medium",
            ),
        ],
        stakeholder_communications=[
            StakeholderCommunication(
                stakeholder_role="Project Coordinator",
                message="Please review the updated event preparation schedule.",
                urgency="high",
                communication_type="email",
            )
        ],
        execution_summary="Coordinate the revised event preparation schedule.",
    )

    mock_artifacts = {
        "recovery_report": "artifacts/recovery_report.pdf",
        "execution_checklist": "artifacts/execution_checklist.md",
        "stakeholder_communications": "artifacts/stakeholder_communications.md    ",
    }

    # Mock AI-powered agents so this test doesn't make API calls.
    monkeypatch.setattr(
        nodes,
        "analyze_disruption",
        lambda **kwargs: disruption,
    )

    monkeypatch.setattr(
        nodes,
        "scout_resources",
        lambda **kwargs: resource_result,
    )

    monkeypatch.setattr(
        nodes,
        "generate_recovery_plan",
        lambda **kwargs: recovery_plan,
    )

    monkeypatch.setattr(
        nodes,
        "review_recovery_plan",
        lambda **kwargs: recovery_review,
    )

    monkeypatch.setattr(
        nodes,
        "generate_execution_plan",
        lambda **kwargs: execution_plan,
    )

    monkeypatch.setattr(
        nodes,
        "generate_execution_artifacts",
        lambda **kwargs: mock_artifacts,
    )

    initial_state = {
        "disruption_description": "Decoration materials will arrive two days late.",
        "project_context": "A project for organizing an event.",
        "project_plan": plan,
        "original_schedule": original_schedule,
    }

    # Act: execute the compiled LangGraph workflow.
    result = waymark_graph.invoke(initial_state)

    # Assert: the workflow produced the expected outputs.
    assert result["disruption"] == disruption

    assert set(result["affected_tasks"]) == {"B", "C", "E"}

    assert isinstance(result["revised_schedule"], Schedule)

    assert result["validation_errors"] == []
    assert result["is_schedule_valid"] is True

    assert result["resource_scout_result"] == resource_result

    assert result["recovery_plan"] == recovery_plan
    assert result["recovery_review"] == recovery_review

    assert result["approved"] is True

    assert result["execution_plan"] == execution_plan
    assert result["execution_artifacts"] == mock_artifacts
