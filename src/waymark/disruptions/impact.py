from waymark.graph.dependencies import get_downstream_tasks
from waymark.schemas.disruption import Disruption
from waymark.schemas.plan import ProjectPlan


def analyze_disruption_impact(
    plan: ProjectPlan,
    disruption: Disruption,
) -> set[str]:
    """Return the disrupted task and all its downstream tasks."""

    task_ids = {task.id for task in plan.tasks}

    if disruption.task_id not in task_ids:
        raise ValueError(f"Unknown task ID: {disruption.task_id}")

    affected_tasks = get_downstream_tasks(
        plan,
        disruption.task_id,
    )

    affected_tasks.add(disruption.task_id)

    return affected_tasks
