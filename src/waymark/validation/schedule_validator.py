from waymark.schemas.plan import ProjectPlan
from waymark.schemas.schedule import Schedule


def validate_schedule(plan: ProjectPlan, schedule: Schedule) -> list[str]:
    """Validate a calculated schedule against project constraints."""

    errors: list[str] = []

    planned_task_ids = {task.id for task in plan.tasks}
    schedule_task_ids = {task.task_id for task in schedule.tasks}

    missing_tasks = planned_task_ids - schedule_task_ids
    unexpected_tasks = schedule_task_ids - planned_task_ids

    for task_id in sorted(missing_tasks):
        errors.append(f"Task '{task_id}' is missing from the schedule.")

    for task_id in sorted(unexpected_tasks):
        errors.append(f"Task '{task_id}' is not part of the project plan.")

    for task in schedule.tasks:
        if task.start_date < plan.start_date:
            errors.append(
                f"Task '{task.task_id}' starts before the project start date."
            )

    for task in schedule.tasks:
        if task.finish_date > plan.deadline:
            errors.append(f"Task '{task.task_id}' finishes after the project deadline.")

    scheduled_tasks_by_id = {task.task_id: task for task in schedule.tasks}

    for task in plan.tasks:
        schedule_task = scheduled_tasks_by_id.get(task.id)

        if schedule_task is None:
            continue

        for dependency_id in task.dependencies:
            dependency = scheduled_tasks_by_id.get(dependency_id)

            if dependency is None:
                continue

            if schedule_task.start_date < dependency.finish_date:
                errors.append(
                    f"Task '{task.id}' starts before dependency '{dependency_id}' finishes."
                )

    return errors
