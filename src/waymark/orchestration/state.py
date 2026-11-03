from typing import NotRequired, TypedDict

from waymark.schemas.disruption import Disruption
from waymark.schemas.execution import ExecutionPlan
from waymark.schemas.plan import ProjectPlan
from waymark.schemas.recovery import RecoveryPlan
from waymark.schemas.resource_scout import ResourceScoutResult
from waymark.schemas.review import RecoveryReview
from waymark.schemas.schedule import Schedule


class WaymarkState(TypedDict):
    # User input
    disruption_description: str
    project_context: str
    project_plan: ProjectPlan
    original_schedule: Schedule

    # Change analysis
    disruption: Disruption
    affected_tasks: list[str]

    # Schedule recovery
    revised_schedule: Schedule
    validation_errors: list[str]
    is_schedule_valid: bool

    # Resource discovery
    resource_scout_result: ResourceScoutResult | None

    # Recovery planning and review
    recovery_plan: RecoveryPlan
    recovery_review: RecoveryReview
    revision_count: NotRequired[int]
    review_feedback: NotRequired[str]

    # Execution
    approved: bool
    execution_artifacts: dict[str, str]
    execution_errors: list[str]
    execution_plan: ExecutionPlan
