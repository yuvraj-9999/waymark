from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class TaskScheduleChange(BaseModel):
    """Represent the scheduling changes for a single task."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    task_id: str = Field(min_length=1)

    original_start: date
    original_finish: date

    revised_start: date
    revised_finish: date

    delay_days: int


class ScheduleComparison(BaseModel):
    """Represent the differnces between two project schedules"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    changes: list[TaskScheduleChange]
