from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from waymark.schemas.task import Task
from waymark.schemas.validators import reject_blank_string


class ProjectPlan(BaseModel):
    """A project definition and its scheduling constraints."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    start_date: date
    deadline: date
    tasks: list[Task] = Field(min_length=1)

    _validate_strings = field_validator("id", "name")(reject_blank_string)

    @model_validator(mode="after")
    def validate_plan(self) -> ProjectPlan:
        if self.deadline < self.start_date:
            raise ValueError("Deadline cannot precede the project start date.")

        task_ids = [task.id for task in self.tasks]

        if len(task_ids) != len(set(task_ids)):
            raise ValueError("Task IDs must be unique within a project.")

        known_ids = set(task_ids)

        for task in self.tasks:
            unknown = set(task.dependencies) - known_ids

            if unknown:
                raise ValueError(
                    f"Task '{task.id}' references unknown dependencies: "
                    f"{sorted(unknown)}"
                )

        return self
