from datetime import timedelta

import networkx as nx

from waymark.graph.dependencies import build_dependency_graph
from waymark.schemas.plan import ProjectPlan
from waymark.schemas.schedule import Schedule, ScheduledTask


def calculate_schedule(plan: ProjectPlan) -> Schedule:
    """Calculate the earliest feasible start dates from task dependencies."""

    graph = build_dependency_graph(plan)

    if not nx.is_directed_acyclic_graph(graph):
        raise ValueError("Cannot schedule a project with circular dependencies.")

    topological_order = list(nx.topological_sort(graph))
    tasks_by_id = {task.id: task for task in plan.tasks}

    scheduled_tasks: dict[str, ScheduledTask] = {}

    for task_id in topological_order:
        task = tasks_by_id[task_id]

        if task.dependencies:
            start_date = max(
                scheduled_tasks[dependency_id].finish_date
                for dependency_id in task.dependencies
            )
        else:
            start_date = plan.start_date

        finish_date = start_date + timedelta(days=task.duration_days)

        scheduled_tasks[task_id] = ScheduledTask(
            task_id=task.id,
            start_date=start_date,
            finish_date=finish_date,
        )
    return Schedule(
        tasks=[scheduled_tasks[task_id] for task_id in nx.topological_sort(graph)]
    )
