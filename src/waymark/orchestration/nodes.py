from waymark.agents.analyst import analyze_disruption
from waymark.agents.repair_planner import generate_recovery_plan
from waymark.agents.resource_scout import scout_resources
from waymark.agents.reviewer import review_recovery_plan
from waymark.disruptions.impact import analyze_disruption_impact
from waymark.orchestration.state import WaymarkState
from waymark.scheduling.replanner import replan_schedule
from waymark.validation.schedule_validator import validate_schedule


def analyst_node(state: WaymarkState) -> dict:
    """Extract structured disruption information."""

    disruption = analyze_disruption(
        disruption_description=state["disruption_description"],
        project_context=state["project_context"],
    )

    known_task_ids = {task.id for task in state["project_plan"].tasks}

    if disruption.task_id not in known_task_ids:
        raise ValueError(
            f"Change Analyst returned unknown task ID: {disruption.task_id}"
        )

    return {"disruption": disruption}


def impact_node(state: WaymarkState) -> dict:
    """Identify the affected tasks."""

    affected_tasks = analyze_disruption_impact(
        plan=state["project_plan"],
        disruption=state["disruption"],
    )

    return {"affected_tasks": affected_tasks}


def replanning_node(state: WaymarkState) -> dict:
    """Calculate the revised schedule deterministically."""

    revised_schedule = replan_schedule(
        plan=state["project_plan"],
        original_schedule=state["original_schedule"],
        disruption=state["disruption"],
    )

    return {"revised_schedule": revised_schedule}


def validation_node(state: WaymarkState) -> dict:
    """Validate the revised schedule."""

    validation_errors = validate_schedule(
        plan=state["project_plan"],
        schedule=state["revised_schedule"],
    )

    return {
        "validation_errors": validation_errors,
        "is_schedule_valid": not validation_errors,
    }


def resource_scout_node(state: WaymarkState) -> dict:
    """Search for alternatives if the disruption requires resources."""

    result = scout_resources(
        disruption_description=state["disruption_description"],
        project_context=state["project_context"],
    )

    return {"resource_scout_result": result}


def repair_planner_node(state: WaymarkState) -> dict:
    """Generate recovery strategies."""

    recovery_plan = generate_recovery_plan(
        plan=state["project_plan"],
        original_schedule=state["original_schedule"],
        disruption=state["disruption"],
        affected_tasks=set(state["affected_tasks"]),
        revised_schedule=state["revised_schedule"],
        validation_errors=state["validation_errors"],
    )

    return {"recovery_plan": recovery_plan}


def reviewer_node(state: WaymarkState) -> dict:
    """Review recovery strategies against project constraints."""

    recovery_review = review_recovery_plan(
        recovery_plan=state["recovery_plan"],
        plan=state["project_plan"],
        affected_tasks=set(state["affected_tasks"]),
        validation_errors=state["validation_errors"],
    )

    return {
        "recovery_review": recovery_review,
        "approved": recovery_review.approved,
    }
