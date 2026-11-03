
from pydantic import BaseModel

from waymark.config import settings
from waymark.llm.gemini_client import client
from waymark.scheduling.comparison import compare_schedules
from waymark.schemas.disruption import Disruption
from waymark.schemas.plan import ProjectPlan
from waymark.schemas.recovery import RecoveryPlan
from waymark.schemas.schedule import Schedule
from waymark.schemas.schedule_comparison import ScheduleComparison


class GeminiRecoveryStrategy(BaseModel):
    """Gemini-compatible recovery strategy schema."""

    name: str
    description: str
    affected_tasks: list[str]
    benefits: list[str]
    risks: list[str]
    assumptions: list[str]


class GeminiRecoveryPlan(BaseModel):
    """Gemini-compatible recovery plan schema."""

    strategies: list[GeminiRecoveryStrategy]
    recommendation: str


def generate_recovery_plan(
    plan: ProjectPlan,
    original_schedule: Schedule,
    disruption: Disruption,
    affected_tasks: set[str],
    revised_schedule: Schedule,
    validation_errors: list[str],
    review_feedback: str | None = None,
    previous_recovery_plan : RecoveryPlan | None = None,
) -> RecoveryPlan:
    """Generate or revise recovery strategies using deterministic analysis."""

    comparison: ScheduleComparison = compare_schedules(
        original_schedule=original_schedule,
        revised_schedule=revised_schedule,
    )

    if review_feedback:
        revision_instructions = f"""
            This is a revision of a previously rejected recovery plan.

            PREVIOUS RECOVERY PLAN:
            {previous_recovery_plan.model_dump_json(indent=2)
            if previous_recovery_plan else "Not available"}

            REVIEWER FEEDBACK:
            {review_feedback}

            You MUST correct every blocking issue identified by the Reviewer.

            Specifically:
            - Correct inaccurate affected_tasks lists in individual strategies.
            - Only include tasks that are genuinely affected by that strategy.
            - Do not confuse all downstream schedule-affected tasks with
                tasks that the strategy directly addresses.
            - Preserve valid strategies where possible.
            - Do not repeat a rejected strategy without correcting its issues.
        """
    else:
        revision_instructions = """
            This is the initial recovery plan.
        """

    prompt = f"""
    You are Waymark's Repair Planner.

    Your responsibility is to propose practical recovery strategies
    for a disrupted project.

    {revision_instructions}

    PROJECT PLAN:
    {plan.model_dump_json(indent=2)}

    ORIGINAL SCHEDULE:
    {original_schedule.model_dump_json(indent=2)}

    DISRUPTION:
    {disruption.model_dump_json(indent=2)}

    AFFECTED TASKS:
    {sorted(affected_tasks)}

    REVISED SCHEDULE:
    {revised_schedule.model_dump_json(indent=2)}

    SCHEDULE COMPARISON:
    {comparison.model_dump_json(indent=2)}

    DETERMINISTIC VALIDATION ERRORS:
    {validation_errors}

    INSTRUCTIONS:

    1. Propose 2 or 3 practical recovery strategies.
    2. Use the supplied schedule and analysis results as facts.
    3. Do not independently calculate or modify task dates.
    4. Task durations are immutable.
    5. Task dependencies are immutable.
    6. Never recommend overtime or additional personnel
       as a justification for reducing task duration.
    7. Do not invent resources or assume their availability.
    8. Clearly distinguish confirmed facts from assumptions.
    9. Consider project deadline implications.
    10. If validation errors exist, address them in the proposed strategies.
    11. Explain benefits, risks, and trade-offs.
    12. Recommend the most appropriate strategy and explain why.
    13. Do not claim resource feasibility without evidence.
    14. Do not claim critical-path status unless supplied as verified data.
    15. Do not execute any proposed actions.
    16. Never claim resource availability has been confirmed
        unless the supplied information explicitly confirms it.
    17. For each strategy, its affected_tasks list must contain only tasks
        directly addressed or impacted by that specific strategy.
    18. Never include tasks that are already completed unless the strategy
        explicitly addresses a completed task.
    19. When revising a strategy, follow the Reviewer's affected-task
        corrections exactly. In particular, exclude tasks the Reviewer
        explicitly identifies as completed and unaffected.
    20. Do not copy the global affected_tasks list into every strategy.
        Strategy-specific affected_tasks must reflect the strategy itself
    21. Before returning the recovery plan, verify that every task ID
        in every strategy's affected_tasks list belongs to the supplied
        AFFECTED TASKS list.
    Return the structured recovery plan.
    """

    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": GeminiRecoveryPlan,
            "temperature": 0.3,
        },
    )

    if not response.text:
        raise ValueError("Gemini returned an empty recovery plan.")

    return RecoveryPlan.model_validate_json(response.text)
