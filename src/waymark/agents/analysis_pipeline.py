from waymark.agents.analyst import analyze_disruption
from waymark.agents.repair_planner import generate_recovery_plan
from waymark.disruptions.impact import analyze_disruption_impact
from waymark.scheduling.replanner import replan_schedule
from waymark.schemas.plan import ProjectPlan
from waymark.schemas.schedule import Schedule
from waymark.validation.schedule_validator import validate_schedule


def process_disruption(
    disruption_description: str,
    project_context: str,
    plan: ProjectPlan,
    original_schedule: Schedule,
) -> dict:
    """Analyze a disruption, replan the schedule, and generate recovery strategies."""

    # 1. Extract structured disruption using Gemini.
    disruption = analyze_disruption(
        disruption_description=disruption_description,
        project_context=project_context,
    )

    known_task_ids = {task.id for task in plan.tasks}

    if disruption.task_id not in known_task_ids:
        raise ValueError(
            f"Change Analyst returned unknown task ID: {disruption.task_id}"
        )

    # 2. Calculate affected tasks deterministically.
    affected_tasks = analyze_disruption_impact(
        plan=plan,
        disruption=disruption,
    )

    # 3. Generate a revised schedule deterministically.
    revised_schedule = replan_schedule(
        plan=plan,
        original_schedule=original_schedule,
        disruption=disruption,
    )

    validation_errors = validate_schedule(
        plan=plan,
        schedule=revised_schedule,
    )

    recovery_plan = generate_recovery_plan(
        plan=plan,
        original_schedule=original_schedule,
        disruption=disruption,
        affected_tasks=set(affected_tasks),
        revised_schedule=revised_schedule,
        validation_errors=validation_errors,
    )

    return {
        "disruption": disruption,
        "affected_tasks": affected_tasks,
        "revised_schedule": revised_schedule,
        "validation_errors": validation_errors,
        "is_schedule_valid": not validation_errors,
        "recovery_plan": recovery_plan,
    }
