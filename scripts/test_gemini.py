from google.genai.errors import APIError
from pydantic import BaseModel, ValidationError

from waymark.config import settings
from waymark.llm.gemini_client import client
from waymark.schemas.analysis import ImpactAnalysis


class GeminiImpactAnalysis(BaseModel):
    """Gemini-compatible schema for structured generation."""

    directly_affected: list[str]
    indirectly_affected: list[str]
    unaffected: list[str]
    explanation: str


prompt = """
Analyze this project disruption.

Tasks:
A: Venue preparation. Unaffected.
B: Stage decoration. Delayed by exactly 2 days.
C: Sound setup. Depends on B.
D: Lighting setup. Depends on A.
E: Final inspection. Depends on C and D.

Return an impact analysis.

B is directly affected.
C and E are indirectly affected.
A and D are unaffected.

Do not invent facts.
Return only the requested structured data.
"""


def main():
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

        if not response.text:
            raise ValueError("Gemini returned an empty response.")

        print("MODEL:", settings.gemini_model)

        print("\nRAW RESPONSE:")
        print(response.text)

        # Validate against Waymark's authoritative schema.
        analysis = ImpactAnalysis.model_validate_json(response.text)

        print("\nPYDANTIC VALIDATION: SUCCESS")
        print(analysis.model_dump_json(indent=2))

    except (APIError, ValidationError, ValueError) as error:
        print("\nGEMINI TEST FAILED:", type(error).__name__)
        print("DETAILS:", error)


if __name__ == "__main__":
    main()
