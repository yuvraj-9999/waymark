from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ExecutionStep(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    step: int = Field(gt=0)
    description: str = Field(min_length=1)
    related_tasks: list[str] = Field(default_factory=list)
    priority: Literal["low", "medium", "high", "critical"]


class StakeholderCommunication(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    stakeholder_role: str = Field(min_length=1)
    message: str = Field(min_length=1)
    urgency: Literal["low", "medium", "high", "critical"]
    communication_type: Literal["email", "meeting_request", "internal_notice"]


class ExecutionPlan(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    action_steps: list[ExecutionStep] = Field(min_length=1)
    stakeholder_communications: list[StakeholderCommunication] = Field(
        default_factory=list
    )
    execution_summary: str = Field(min_length=1)
