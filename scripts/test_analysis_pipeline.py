from datetime import date

from waymark.agents.analysis_pipeline import process_disruption
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


def main():
    result = process_disruption(
        disruption_description=(
            "Task B's start is delayed by exactly 2 calendar days. "
            "Its duration remains unchanged."
        ),
        project_context="""
        Task A: Venue preparation
        Task B: Stage decoration, depends on A
        Task C: Sound setup, depends on B
        Task D: Lighting setup, depends on A
        Task E: Final inspection, depends on C and D
        """,
        plan=plan,
        original_schedule=original_schedule,
    )

    print("\nDISRUPTION:")
    print(result["disruption"].model_dump_json(indent=2))

    print("\nAFFECTED TASKS:")
    print(sorted(result["affected_tasks"]))

    print("\nREVISED SCHEDULE:")
    for task in result["revised_schedule"].tasks:
        print(f"{task.task_id}: {task.start_date} -> {task.finish_date}")

    assert result["affected_tasks"] == {"B", "C", "E"}

    revised = {task.task_id: task for task in result["revised_schedule"].tasks}

    assert revised["B"].start_date == date(2026, 12, 5)
    assert revised["B"].finish_date == date(2026, 12, 7)
    assert revised["C"].start_date == date(2026, 12, 7)
    assert revised["E"].finish_date == date(2026, 12, 10)
    assert result["validation_errors"] == []
    assert result["is_schedule_valid"] is True

    print("\nVALIDATION:")
    print("Errors:", result["validation_errors"])
    print("Schedule valid:", result["is_schedule_valid"])

    print("\nALL PIPELINE CHECKS PASSED!")


if __name__ == "__main__":
    main()
