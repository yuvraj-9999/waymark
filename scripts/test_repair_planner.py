from datetime import date

from waymark.agents.repair_planner import generate_recovery_plan
from waymark.schemas.disruption import Disruption
from waymark.schemas.plan import ProjectPlan
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
            finish_date=date(2026, 12, 5),
        ),
        ScheduledTask(
            task_id="E",
            start_date=date(2026, 12, 7),
            finish_date=date(2026, 12, 8),
        ),
    ],
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


def main():
    disruption = Disruption(
        task_id="B",
        delay_days=2,
        reason="Stage decoration start delayed by 2 days",
    )

    recovery_plan = generate_recovery_plan(
        plan=plan,
        original_schedule=original_schedule,
        disruption=disruption,
        affected_tasks={"B", "C", "E"},
        revised_schedule=revised_schedule,
        validation_errors=[],
    )

    print("\nREPAIR PLANNER RESULT")
    print("=" * 60)

    print(recovery_plan.model_dump_json(indent=2))

    assert len(recovery_plan.strategies) >= 1
    assert recovery_plan.recommendation.strip()

    for strategy in recovery_plan.strategies:
        assert strategy.name.strip()
        assert strategy.description.strip()

    print("\nALL REPAIR PLANNER CHECKS PASSED!")


if __name__ == "__main__":
    main()
