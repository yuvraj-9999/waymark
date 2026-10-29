from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from waymark.schemas.validators import reject_blank_string


class ScheduledTask(BaseModel):
    """The calculated dates for a task in a project schedule."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    task_id: str = Field(min_length=1)
    start_date: date
    finish_date: date

    _validate_strings = field_validator("task_id")(reject_blank_string)

    @model_validator(mode="after")
    def validate_date_range(self) -> "ScheduledTask":
        if self.finish_date <= self.start_date:
            raise ValueError("Finish date must be after start date.")

        return self


class Schedule(BaseModel):
    """The calculated schedule for a project."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    tasks: list[ScheduledTask] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_task_ids(self) -> "Schedule":
        task_ids = [task.task_id for task in self.tasks]

        if len(task_ids) != len(set(task_ids)):
            raise ValueError("Scheduled task IDs must be unique.")

        return self
