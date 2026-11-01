from pydantic import BaseModel

from waymark.config import settings
from waymark.llm.gemini_client import client
from waymark.schemas.disruption import Disruption


class GeminiDisruption(BaseModel):
    """Gemini-compatible schema for disruption extraction."""

    task_id: str
    delay_days: int
    reason: str


def analyze_disruption(
    disruption_description: str,
    project_context: str,
) -> Disruption:
    """Extract a structured task-delay disruption from natural language."""

    prompt = f"""
    You are Waymark's Change Analyst.

    Extract the task delay described in the disruption.

    PROJECT CONTEXT:
    {project_context}

    DISRUPTION:
    {disruption_description}

    RULES:
    - Extract the exact task ID from the project context.    
    - Task IDs are identifiers such as A, B, C, not task names    .
    - Never include words like "Task" in the task_id fiel    d.
    - The task_id must exactly match an ID supplied in the project context.
    - Extract the delay in calendar days.
    - Do not confuse a start delay with a duration increase.
    - Do not invent missing information.
    - This function currently supports positive task delays only.
    - If the disruption does not clearly describe a supported task delay,
      do not fabricate a result.

    Return the structured disruption.
    """

    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": GeminiDisruption,
            "temperature": 0.1,
        },
    )

    if not response.text:
        raise ValueError("Gemini returned an empty disruption analysis.")

    return Disruption.model_validate_json(response.text)
