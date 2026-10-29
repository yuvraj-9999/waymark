from __future__ import annotations

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from waymark.schemas.validators import reject_blank_string


class Task(BaseModel):
    """A unit of work within a project."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    duration_days: int = Field(gt=0)
    dependencies: list[str] = Field(default_factory=list)

    _validate_strings = field_validator("id", "name")(reject_blank_string)

    @model_validator(mode="after")
    def validate_dependencies(self) -> Task:
        if self.id in self.dependencies:
            raise ValueError("A task cannot depend on itself.")

        if len(self.dependencies) != len(set(self.dependencies)):
            raise ValueError("Duplicate dependencies are not allowed.")

        if any(not dependency.strip() for dependency in self.dependencies):
            raise ValueError("Dependency IDs cannot be empty.")

        return self
