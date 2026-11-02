from pydantic import BaseModel

from waymark.config import settings
from waymark.llm.gemini_client import client
from waymark.llm.serpapi_client import search_web
from waymark.schemas.resource_scout import (
    ResourceCandidate,
    ResourceScoutResult,
    ResourceSearchRequest,
)


class GeminiResourceSearchRequest(BaseModel):
    """Gemini-compatible schema for resource search decisions."""

    search_required: bool
    resource_type: str
    search_query: str
    location: str
    explanation: str


def scout_resources(
    disruption_description: str,
    project_context: str,
) -> ResourceScoutResult:
    """Identify whether resource discovery is needed and search for alternatives."""

    prompt = f"""
    You are Waymark's Resource Scout.

    Determine whether the disruption requires finding an alternative
    physical resource, venue, equipment, supplier, or service.

    PROJECT CONTEXT:
    {project_context}

    DISRUPTION:
    {disruption_description}

    RULES:
    - Search only when finding an alternative resource is relevant.
    - Ordinary task delays do not require resource searching.
    - Do not search for alternative people or team members.
    - Do not invent resources or availability.
    - If searching is required, generate a concise Google search query.
    - Use the location from the project context when available.
    - If the location is unknown, leave it empty.
    - Explain your decision.

    Return the structured result.
    """

    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": GeminiResourceSearchRequest,
            "temperature": 0.1,
        },
    )

    if not response.text:
        raise ValueError("Gemini returned an empty resource search decision.")

    request = ResourceSearchRequest.model_validate_json(response.text)

    if not request.search_required:
        return ResourceScoutResult(
            search_performed=False,
            explanation=request.explanation,
        )

    if not request.search_query.strip():
        raise ValueError(
            "Resource Scout required a search but feturned an empty query."
        )

    results = search_web(
        query=request.search_query,
        location=request.location or None,
        num_results=5,
    )

    candidates = [
        ResourceCandidate(
            title=result.get("title") or "Untitled result",
            url=result.get("link") or "",
            snippet=result.get("snippet") or "",
            source=result.get("source") or "",
            availability_confirmed=False,
        )
        for result in results
        if result.get("link")
    ]

    return ResourceScoutResult(
        search_performed=True,
        search_query=request.search_query,
        explanation=request.explanation,
        candidates=candidates,
    )
