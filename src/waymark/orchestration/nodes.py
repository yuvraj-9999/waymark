from waymark.agents.analyst import analyze_disruption
from waymark.agents.execution import generate_execution_plan
from waymark.agents.repair_planner import generate_recovery_plan
from waymark.agents.resource_scout import scout_resources
from waymark.agents.reviewer import review_recovery_plan
from waymark.artifacts.execution_artifacts import generate_execution_artifacts
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
    """Generate or revise recovery strategies."""

    recovery_plan = generate_recovery_plan(
        plan=state["project_plan"],
        original_schedule=state["original_schedule"],
        disruption=state["disruption"],
        affected_tasks=set(state["affected_tasks"]),
        revised_schedule=state["revised_schedule"],
        validation_errors=state["validation_errors"],
        review_feedback=state.get("review_feedback"),
        previous_recovery_plan=state.get("recovery_plan"),
    )

    return {
        "recovery_plan": recovery_plan,
        "revision_count": state.get("revision_count", 0) + 1,
    }


def reviewer_node(state: WaymarkState) -> dict:
    """Review recovery strategies against project constraints."""

    recovery_review = review_recovery_plan(
        recovery_plan=state["recovery_plan"],
        plan=state["project_plan"],
        affected_tasks=set(state["affected_tasks"]),
        validation_errors=state["validation_errors"],
    )

    feedback_parts = [
        recovery_review.overall_assessment,
    ]

    for strategy_review in recovery_review.strategy_reviews:
        feedback_parts.append(
            f"Strategy: {strategy_review.strategy_name}\n"
            f"Acceptable: {strategy_review.is_acceptable}\n"
            f"Severity: {strategy_review.severity}\n"
            f"Issues: {'; '.join(strategy_review.issues) or 'None'}\n"
            f"Suggestions: {'; '.join(strategy_review.suggestions) or 'None'}"
        )

    review_feedback = "\n\n".join(feedback_parts)

    return {
        "recovery_review": recovery_review,
        "approved": recovery_review.approved,
        "review_feedback": review_feedback,
    }


def execution_node(state: WaymarkState) -> dict:
    """Generate execution steps and stakeholder communication drafts."""

    if not state["approved"]:
        raise ValueError(
            "Cannot generate an execution plan for an unapproved recovery plan."
        )

    execution_plan = generate_execution_plan(
        plan=state["project_plan"],
        disruption=state["disruption"],
        affected_tasks=state["affected_tasks"],
        revised_schedule=state["revised_schedule"],
        recovery_plan=state["recovery_plan"],
        recovery_review=state["recovery_review"],
    )

    return {"execution_plan": execution_plan}


def artifact_node(state: WaymarkState) -> dict:
    """Generate downloadable recovery and execution artifacts."""

    if not state["approved"]:
        raise ValueError("Cannot generate artifacts for an unapproved recovery plan.")

    execution_artifacts = generate_execution_artifacts(
        plan=state["project_plan"],
        disruption=state["disruption"],
        affected_tasks=state["affected_tasks"],
        original_schedule=state["original_schedule"],
        revised_schedule=state["revised_schedule"],
        recovery_plan=state["recovery_plan"],
        recovery_review=state["recovery_review"],
        execution_plan=state["execution_plan"],
        resource_scout_result=state.get("resource_scout_result"),
    )

    return {"execution_artifacts": execution_artifacts}
