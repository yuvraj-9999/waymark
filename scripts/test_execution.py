from datetime import date

from waymark.agents.execution import generate_execution_plan
from waymark.schemas.disruption import Disruption
from waymark.schemas.execution import ExecutionPlan
from waymark.schemas.plan import ProjectPlan
from waymark.schemas.recovery import RecoveryPlan, RecoveryStrategy
from waymark.schemas.review import RecoveryReview, StrategyReview
from waymark.schemas.schedule import Schedule, ScheduledTask

plan = ProjectPlan(
    id="tech-fest",
    name="Tech Fest",
    start_date=date(2026, 12, 1),
    deadline=date(2026, 12, 10),
    tasks=[
        {
            "id": "A",
            "name": "Venue preparation",
            "duration_days": 2,
            "dependencies": [],
        },
        {
            "id": "B",
            "name": "Stage decoration",
            "duration_days": 2,
            "dependencies": ["A"],
        },
        {
            "id": "C",
            "name": "Sound setup",
            "duration_days": 2,
            "dependencies": ["B"],
        },
        {
            "id": "D",
            "name": "Lighting setup",
            "duration_days": 2,
            "dependencies": ["A"],
        },
        {
            "id": "E",
            "name": "Final inspection",
            "duration_days": 1,
            "dependencies": ["C", "D"],
        },
    ],
)

disruption = Disruption(
    task_id="B",
    delay_days=2,
    reason="Stage decoration start delayed by 2 days",
)

revised_schedule = Schedule(
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
        ScheduledTask(
            task_id="D",
            start_date=date(2026, 12, 3),
            finish_date=date(2026, 12, 5),
        ),
        ScheduledTask(
            task_id="E",
            start_date=date(2026, 12, 9),
            finish_date=date(2026, 12, 10),
        ),
    ],
)

recovery_plan = RecoveryPlan(
    strategies=[
        RecoveryStrategy(
            name="Resequence preparation",
            description="Coordinate preparation activities around the delayed decoration task.",
            affected_tasks=["B", "C", "E"],
            benefits=["Keeps the revised schedule visible to stakeholders."],
            risks=["Requires coordination between teams."],
            assumptions=["Teams can follow the revised task sequence."],
        )
    ],
    recommendation="Use the revised schedule and coordinate affected activities.",
)

recovery_review = RecoveryReview(
    strategy_reviews=[
        StrategyReview(
            strategy_name="Resequence preparation",
            is_acceptable=True,
            issues=[],
            suggestions=[],
            severity="none",
        )
    ],
    overall_assessment="The recovery strategy is acceptable.",
    approved=True,
)


def main():
    execution_plan = generate_execution_plan(
        plan=plan,
        disruption=disruption,
        affected_tasks=["B", "C", "E"],
        revised_schedule=revised_schedule,
        recovery_plan=recovery_plan,
        recovery_review=recovery_review,
    )

    print("\nEXECUTION AGENT RESULT")
    print("=" * 60)
    print(execution_plan.model_dump_json(indent=2))

    assert isinstance(execution_plan, ExecutionPlan)
    assert len(execution_plan.action_steps) >= 1
    assert execution_plan.execution_summary.strip()

    print("\nALL EXECUTION AGENT CHECKS PASSED!")


if __name__ == "__main__":
    main()
