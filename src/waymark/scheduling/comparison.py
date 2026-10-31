from waymark.schemas.schedule import Schedule
from waymark.schemas.schedule_comparison import ScheduleComparison, TaskScheduleChange


def compare_schedules(
    original_schedule: Schedule, revised_schedule: Schedule
) -> ScheduleComparison:
    """Compare two schedules and identify changes to task dates."""

    original_tasks = {task.task_id: task for task in original_schedule.tasks}

    revised_tasks = {task.task_id: task for task in revised_schedule.tasks}

    if original_tasks.keys() != revised_tasks.keys():
        raise ValueError("Original and revised schedules must contain the same tasks.")

    changes = []

    for task_id, original_task in original_tasks.items():
        revised_task = revised_tasks[task_id]

        delay_days = (revised_task.finish_date - original_task.finish_date).days

        changes.append(
            TaskScheduleChange(
                task_id=task_id,
                original_start=original_task.start_date,
                original_finish=original_task.finish_date,
                revised_start=revised_task.start_date,
                revised_finish=revised_task.finish_date,
                delay_days=delay_days,
            )
        )

    return ScheduleComparison(changes=changes)
