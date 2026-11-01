import time

from pydantic import BaseModel, ValidationError

from waymark.config import settings
from waymark.llm.gemini_client import client
from waymark.schemas.analysis import ImpactAnalysis


class GeminiImpactAnalysis(BaseModel):
    """Gemini-compatible structured output schema."""

    directly_affected: list[str]
    indirectly_affected: list[str]
    unaffected: list[str]
    explanation: str


class BenchmarkError(Exception):
    """Raised when Gemini benchmarking fails."""


def run_benchmark(prompt: str) -> dict:
    start_time = time.perf_counter()

    try:
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": GeminiImpactAnalysis,
                "temperature": 0.2,
            },
        )

        latency = time.perf_counter() - start_time

        if not response.text:
            raise BenchmarkError("Gemini returned an empty response.")

        # Validate Gemini's output against Waymark's authoritative schema.
        analysis = ImpactAnalysis.model_validate_json(response.text)

        usage = response.usage_metadata

        return {
            "model": settings.gemini_model,
            "analysis": analysis,
            "latency_seconds": round(latency, 2),
            "tokens_used": (usage.total_token_count if usage else None),
        }

    except (ValidationError, ValueError, BenchmarkError) as error:
        raise BenchmarkError(str(error)) from error
