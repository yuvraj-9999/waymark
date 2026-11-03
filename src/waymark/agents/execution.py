import json

from pydantic import BaseModel

from waymark.config import settings
from waymark.llm.gemini_client import client
from waymark.schemas.disruption import Disruption
from waymark.schemas.execution import ExecutionPlan
from waymark.schemas.plan import ProjectPlan
from waymark.schemas.recovery import RecoveryPlan
from waymark.schemas.review import RecoveryReview
from waymark.schemas.schedule import Schedule


class GeminiExecutionStep(BaseModel):
    """Gemini-compatible execution step schema."""

    step: int
    description: str
    related_tasks: list[str]
    priority: str


class GeminiStakeholderCommunication(BaseModel):
    """Gemini-compatible stakeholder communication schema."""

    stakeholder_role: str
    message: str
    urgency: str
    communication_type: str


class GeminiExecutionPlan(BaseModel):
    """Gemini-compatible execution plan schema."""

    action_steps: list[GeminiExecutionStep]
    stakeholder_communications: list[GeminiStakeholderCommunication]
    execution_summary: str


def generate_execution_plan(
    plan: ProjectPlan,
    disruption: Disruption,
    affected_tasks: list[str],
    revised_schedule: Schedule,
    recovery_plan: RecoveryPlan,
    recovery_review: RecoveryReview,
) -> ExecutionPlan:
    """Generate execution instructions for an approved recovery plan."""

    if not recovery_review.approved:
        raise ValueError(
            "Cannot generate an execution plan for an unapproved recovery plan."
        )

    prompt = f"""
    You are Waymark's Execution Agent.

    Your responsibility is to turn an approved recovery plan into
    concrete, actionable execution instructions and stakeholder
    communication drafts.

    PROJECT PLAN:
    {plan.model_dump_json(indent=2)}

    DISRUPTION:
    {disruption.model_dump_json(indent=2)}

    AFFECTED TASKS:
    {affected_tasks}

    REVISED SCHEDULE:
    {revised_schedule.model_dump_json(indent=2)}

    APPROVED RECOVERY PLAN:
    {recovery_plan.model_dump_json(indent=2)}

    REVIEW:
    {recovery_review.model_dump_json(indent=2)}

    INSTRUCTIONS:

    1. Generate clear, practical, ordered action steps.
    2. Each action step must have a positive step number.
    3. Reference relevant task IDs whenever possible.
    4. Assign an appropriate priority to every action.
    5. Generate stakeholder communication drafts when useful.
    6. Specify the stakeholder's role, not an invented person's name.
    7. Communication types must be email, meeting_request,
       or internal_notice.
    8. Communication urgency must be low, medium, high, or critical.
    9. Do not invent stakeholder names, contact details, or resources.
    10. Do not claim that any action has already been completed.
    11. Do not claim that resource availability has been confirmed.
    12. Do not modify task durations, dependencies, or schedule dates.
    13. Do not contradict the approved recovery plan.
    14. Do not send emails or perform external actions.
    15. All communications are drafts requiring human review.
    16. Keep the execution summary concise and informative.

    Return the structured execution plan.
    """

    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": GeminiExecutionPlan,
            "temperature": 0.3,
        },
    )

    if not response.text:
        raise ValueError("Gemini returned an empty execution plan.")

    execution_data = json.loads(response.text)

    for step in execution_data.get("action_steps", []):
        step["priority"] = step["priority"].lower()

    for communication in execution_data.get("stakeholder_communications", []):
        communication["urgency"] = communication["urgency"].lower()
        communication["communication_type"] = (
            communication["communication_type"].lower().strip().replace(" ", "_")
        )

    return ExecutionPlan.model_validate(execution_data)
