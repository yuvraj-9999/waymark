from pydantic import BaseModel, ConfigDict, Field, field_validator

from waymark.schemas.validators import reject_blank_string


class StrategyReview(BaseModel):
    """Review result for an individual recovery strategy."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    strategy_name: str = Field(min_length=1)
    is_acceptable: bool
    issues: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    severity: str = Field(
        default="none",
        pattern="^(none|warning|blocking)$",
    )

    _validate_strings = field_validator("strategy_name")(reject_blank_string)


class RecoveryReview(BaseModel):
    """Overall review of the proposed recovery plan."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    strategy_reviews: list[StrategyReview] = Field(min_length=1)
    overall_assessment: str = Field(min_length=1)
    approved: bool

    _validate_assessment = field_validator("overall_assessment")(reject_blank_string)
