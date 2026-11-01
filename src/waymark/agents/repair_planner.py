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
) -> RecoveryPlan:
    """Generate recovery strategies using deterministic analysis result."""

    comparison: ScheduleComparison = compare_schedules(
        original_schedule=original_schedule,
        revised_schedule=revised_schedule,
    )

    prompt = f"""
    You are Waymark's Repair Planner.

    Your responsibility is to propose practical recovery strategies
    for a disrupted project.

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
    6. Never recommend overtime or additional person    nel
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
        raise ValueError("Gemini returnedan empty recovery plan.")

    return RecoveryPlan.model_validate_json(response.text)
