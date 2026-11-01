from pydantic import BaseModel, ConfigDict, Field


class ImpactAnalysis(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    directly_affected: list[str] = Field(default_factory=list)
    indirectly_affected: list[str] = Field(default_factory=list)
    unaffected: list[str] = Field(default_factory=list)
    explanation: str
