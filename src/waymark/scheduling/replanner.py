import networkx as nx

from datetime import timedelta

from waymark.disruptions.impact import analyze_disruption_impact
from waymark.graph.dependencies import build_dependency_graph
from waymark.schemas.disruption import Disruption
from waymark.schemas.plan import ProjectPlan
from waymark.schemas.schedule import Schedule, ScheduledTask

def replan_schedule(plan: ProjectPlan, original_schedule: Schedule, disruption: Disruption) -> Schedule:
    """Generate a revised schedule while minimizing unnecessary changes."""

    affected_tasks = analyze_disruption_impact(plan,disruption)

    graph = build_dependency_graph(plan)

    original_tasks = {task.task_id:task for task in original_schedule.tasks}

    plan_tasks = {
        task.id:task for task in plan.tasks
    }

    scheduled_tasks: dict[str, ScheduledTask] = {}

    for task_id, scheduled_task in original_tasks.items():
        if task_id not in affected_tasks:
            scheduled_tasks[task_id] = scheduled_task

    affected_graph = graph.subgraph(affected_tasks)

    topological_order = list(
        nx.topological_sort(affected_graph)
    )

    for task_id in topological_order:
        task = plan_tasks[task_id]
        original_task = original_tasks[task_id]

        dependency_finish_dates = [
            scheduled_tasks[dependency_id].finish_date
            for dependency_id in task.dependencies
        ]

        earliest_start = max(
            [original_task.start_date, *dependency_finish_dates]
        )

        if task_id == disruption.task_id:
            delayed_start = (
                original_task.start_date + timedelta(
                    days = disruption.delay_days
                )
            )

            earliest_start = max(
                earliest_start, delayed_start
            )

        finish_date = earliest_start + timedelta(days=task.duration_days)

        scheduled_tasks[task_id] = ScheduledTask(
            task_id = task_id,
            start_date = earliest_start,
            finish_date= finish_date,
        )

    return Schedule(
        tasks = [
            scheduled_tasks[task.id]
            for task in plan.tasks
        ]
    )