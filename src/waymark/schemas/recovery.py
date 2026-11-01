from pydantic import BaseModel, ConfigDict, Field, field_validator

from waymark.schemas.validators import reject_blank_string


class RecoveryStrategy(BaseModel):
    """A proposed strategy for recovering a disrupted project."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    affected_tasks: list[str] = Field(default_factory=list)
    benefits: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)

    _validate_strings = field_validator(
        "name",
        "description",
    )(reject_blank_string)


class RecoveryPlan(BaseModel):
    """Collection of proposed strategies for project recovery."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    strategies: list[RecoveryStrategy] = Field(min_length=1)
    recommendation: str = Field(min_length=1)

    _validate_recommendation = field_validator(
        "recommendation",
    )(reject_blank_string)
