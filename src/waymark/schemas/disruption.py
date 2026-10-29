from pydantic import BaseModel, ConfigDict, Field, field_validator

from waymark.schemas.validators import reject_blank_string


class Disruption(BaseModel):
    """A delay affecting a task in a project."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    task_id: str = Field(min_length=1)
    delay_days: int = Field(gt=0)
    reason: str = Field(min_length=1)

    _validate_strings = field_validator("task_id", "reason")(reject_blank_string)
