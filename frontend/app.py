from datetime import date
from pathlib import Path

import streamlit as st

from waymark.orchestration.graph import waymark_graph
from waymark.scheduling.scheduler import calculate_schedule
from waymark.schemas.disruption import Disruption
from waymark.schemas.plan import ProjectPlan
from waymark.schemas.task import Task

st.set_page_config(
    page_title="Waymark | Project Recovery",
    page_icon=":material/route:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background-color: #F5F6F8;
        color: #172033;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }

    .waymark-brand {
        font-size: 1.8rem;
        font-weight: 700;
        color: #172B4D;
        letter-spacing: -0.7px;
    }

    .waymark-subtitle {
        color: #64748B;
        font-size: 0.95rem;
        margin-top: 0.25rem;
    }

    .section-label {
        color: #64748B;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    div.stButton > button[kind="primary"] {
        background: #1E3A5F;
        border: 1px solid #1E3A5F;
        border-radius: 6px;
        font-weight: 600;
    }

    div.stButton > button[kind="primary"]:hover {
        background: #274B76;
        border-color: #274B76;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="waymark-brand">WAYMARK</div>
    <div class="waymark-subtitle">
        Project disruption analysis and recovery planning
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

st.markdown("### Create your project")
st.markdown("Define your project, add its tasks, and establish dependencies.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "project_plan" not in st.session_state:
    st.session_state.project_plan = None

if "workflow_result" not in st.session_state:
    st.session_state.workflow_result = None

st.markdown(
    '<div class="section-label">01 / Project details</div>',
    unsafe_allow_html=True,
)

with st.container(border=True):
    project_name = st.text_input(
        "Project name",
        placeholder="Website Development",
    )

    col1, col2 = st.columns(2)

    with col1:
        project_start = st.date_input(
            "Project start date",
            value=date.today(),
        )

    with col2:
        project_deadline = st.date_input(
            "Project deadline",
            value=date.today(),
        )

st.markdown(
    '<div class="section-label">02 / Define tasks</div>',
    unsafe_allow_html=True,
)

with st.container(border=True):
    task_name = st.text_input(
        "Task name",
        placeholder="Design UI",
        key="new_task_name",
    )

    col1, col2 = st.columns(2)

    with col1:
        task_duration = st.number_input(
            "Duration (days)",
            min_value=1,
            value=3,
            step=1,
        )

    task_options = {
        task["id"]: f"{task['name']} ({task['id']})" for task in st.session_state.tasks
    }

    with col2:
        task_dependencies = st.multiselect(
            "Depends on",
            options=list(task_options.keys()),
            format_func=lambda task_id: task_options[task_id],
        )

    if st.button("Add task", icon=":material/add:"):
        if not task_name.strip():
            st.warning("Enter a task name first.")

        elif any(
            task["name"].casefold() == task_name.strip().casefold()
            for task in st.session_state.tasks
        ):
            st.warning("A task with this name already exists.")

        else:
            existing_ids = {
                int(task["id"].split("-")[-1]) for task in st.session_state.tasks
            }

            next_id = max(existing_ids, default=0) + 1
            task_id = f"TASK-{next_id:03d}"

            st.session_state.tasks.append(
                {
                    "id": task_id,
                    "name": task_name.strip(),
                    "duration_days": int(task_duration),
                    "dependencies": task_dependencies,
                }
            )

            st.session_state.project_plan = None
            st.session_state.workflow_result = None
            st.session_state.pop("original_schedule", None)
            st.session_state.pop("disruption", None)
            st.session_state.pop("disruption_context", None)

            st.rerun()

if st.session_state.tasks:
    st.markdown("#### Added tasks")

    task_options = {
        task["id"]: f"{task['name']} ({task['id']})" for task in st.session_state.tasks
    }

    task_rows = [
        {
            "ID": task["id"],
            "Task": task["name"],
            "Duration": f"{task['duration_days']} days",
            "Dependencies": ", ".join(
                task_options.get(dependency, dependency)
                for dependency in task["dependencies"]
            )
            or "None",
        }
        for task in st.session_state.tasks
    ]

    st.dataframe(
        task_rows,
        use_container_width=True,
        hide_index=True,
    )

    task_to_remove = st.selectbox(
        "Remove a task",
        options=[task["id"] for task in st.session_state.tasks],
        format_func=lambda task_id: task_options[task_id],
    )

    if st.button("Remove selected task"):
        st.session_state.tasks = [
            task for task in st.session_state.tasks if task["id"] != task_to_remove
        ]

        for task in st.session_state.tasks:
            task["dependencies"] = [
                dependency
                for dependency in task["dependencies"]
                if dependency != task_to_remove
            ]

        st.session_state.project_plan = None
        st.session_state.workflow_result = None
        st.session_state.pop("original_schedule", None)
        st.session_state.pop("disruption", None)
        st.session_state.pop("disruption_context", None)

        st.rerun()

st.divider()

if st.button(
    "Generate project schedule",
    type="primary",
    use_container_width=True,
):
    if not project_name.strip():
        st.error("Enter a project name.")

    elif project_deadline <= project_start:
        st.error("The deadline must be after the project start date.")

    elif not st.session_state.tasks:
        st.error("Add at least one task.")

    else:
        try:
            tasks = [Task(**task) for task in st.session_state.tasks]

            project_plan = ProjectPlan(
                id="WAYMARK-PROJECT",
                name=project_name.strip(),
                start_date=project_start,
                deadline=project_deadline,
                tasks=tasks,
            )

            original_schedule = calculate_schedule(project_plan)

            st.session_state.project_plan = project_plan
            st.session_state.original_schedule = original_schedule
            st.session_state.workflow_result = None

            st.session_state.pop("disruption", None)
            st.session_state.pop("disruption_context", None)

            st.success("Project schedule generated successfully.")

        except Exception as exc:  # noqa: BLE001
            st.error(f"Unable to generate schedule: {exc}")

if st.session_state.project_plan is not None:
    project_plan = st.session_state.project_plan
    original_schedule = st.session_state.original_schedule

    st.markdown(
        '<div class="section-label">03 / Baseline schedule</div>',
        unsafe_allow_html=True,
    )

    st.markdown("### Baseline schedule")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total tasks", len(project_plan.tasks))
    col2.metric("Project start", str(project_plan.start_date))
    col3.metric("Deadline", str(project_plan.deadline))

    task_names = {task.id: task.name for task in project_plan.tasks}

    schedule_rows = [
        {
            "Task": task_names[scheduled.task_id],
            "Start": scheduled.start_date,
            "Finish": scheduled.finish_date,
        }
        for scheduled in original_schedule.tasks
    ]

    st.dataframe(
        schedule_rows,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    st.markdown(
        '<div class="section-label">04 / Project disruption</div>',
        unsafe_allow_html=True,
    )

    st.markdown("### What happened to your project?")
    st.markdown("Describe the disruption affecting your project schedule.")

    task_options = {task.id: f"{task.name} ({task.id})" for task in project_plan.tasks}

    with st.container(border=True):
        selected_task_id = st.selectbox(
            "Affected task",
            options=list(task_options.keys()),
        )

        delay_days = st.number_input(
            "Expected delay (days)",
            min_value=1,
            value=2,
            step=1,
        )

        disruption_reason = st.text_area(
            "Reason for disruption",
            placeholder=(
                "Example: The frontend developer is unavailable due to illness."
            ),
            height=100,
        )

        disruption_context = st.text_area(
            "Additional context (optional)",
            placeholder=(
                "Describe resource constraints, dependencies, "
                "or other relevant circumstances."
            ),
            height=80,
        )

        if st.button(
            "Confirm disruption",
            type="primary",
            use_container_width=True,
        ):
            if not disruption_reason.strip():
                st.error("Please describe the reason for disruption.")

            else:
                try:
                    disruption = Disruption(
                        task_id=selected_task_id,
                        delay_days=int(delay_days),
                        reason=disruption_reason.strip(),
                    )

                    st.session_state.disruption = disruption
                    st.session_state.disruption_context = disruption_context.strip()
                    st.session_state.workflow_result = None

                    st.success("Disruption details saved.")

                except Exception as exc:  # noqa: BLE001
                    st.error(f"Invalid disruption: {exc}")

    if "disruption" in st.session_state:
        disruption = st.session_state.disruption

        st.markdown("#### Confirmed disruption")

        st.write(f"**Affected task:** {task_options[disruption.task_id]}")

        st.write(f"**Delay:** {disruption.delay_days} days")
        st.write(f"**Reason:** {disruption.reason}")

        if st.button(
            "Analyze disruption",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.workflow_result = None

            disruption_description = (
                f"Task {disruption.task_id} is delayed by "
                f"{disruption.delay_days} days. "
                f"Reason: {disruption.reason}"
            )

            initial_state = {
                "disruption_description": disruption_description,
                "project_context": st.session_state.disruption_context,
                "project_plan": st.session_state.project_plan,
                "original_schedule": st.session_state.original_schedule,
            }

            try:
                with st.spinner(
                    "Waymark is analyzing the disruption and "
                    "generating recovery strategies..."
                ):
                    result = waymark_graph.invoke(initial_state)

                st.session_state.workflow_result = result

                st.success("Disruption analysis completed.")

            except Exception as exc:  # noqa: BLE001
                st.error(f"Workflow failed: {exc}")

if st.session_state.workflow_result is not None:
    result = st.session_state.workflow_result

    st.divider()

    st.markdown(
        '<div class="section-label">05 / Impact analysis</div>',
        unsafe_allow_html=True,
    )

    st.markdown("### Disruption impact")

    affected_tasks = result.get("affected_tasks", [])

    st.write("**Affected tasks:**")

    if affected_tasks:
        affected_task_names = {
            task.id: task.name for task in st.session_state.project_plan.tasks
        }

        for task_id in affected_tasks:
            st.write(f"- {affected_task_names.get(task_id, task_id)} ({task_id})")

    else:
        st.info("No affected tasks were returned.")

    revised_schedule = result.get("revised_schedule")

    if revised_schedule:
        st.markdown("### Revised schedule")

        task_names = {
            task.id: task.name for task in st.session_state.project_plan.tasks
        }

        revised_rows = [
            {
                "Task": task_names.get(task.task_id, task.task_id),
                "Start": task.start_date,
                "Finish": task.finish_date,
            }
            for task in revised_schedule.tasks
        ]

        st.dataframe(
            revised_rows,
            use_container_width=True,
            hide_index=True,
        )

    if result.get("is_schedule_valid"):
        st.success("The revised schedule passed validation.")

    else:
        st.warning("The revised schedule has validation issues.")

        for error in result.get("validation_errors", []):
            st.write(f"- {error}")

    st.divider()

    st.markdown(
        '<div class="section-label">06 / Resource discovery</div>',
        unsafe_allow_html=True,
    )

    st.markdown("### Alternative resources")

    resource_scout_result = result.get("resource_scout_result")

    if resource_scout_result:
        if not resource_scout_result.search_performed:
            st.info(resource_scout_result.explanation)

        else:
            st.caption(f"Search query: {resource_scout_result.search_query}")

            st.write(resource_scout_result.explanation)

            if resource_scout_result.candidates:
                for index, candidate in enumerate(
                    resource_scout_result.candidates,
                    start=1,
                ):
                    candidate_title = candidate.title or f"Resource candidate {index}"

                    with st.expander(candidate_title):
                        if candidate.source:
                            st.caption(f"Source: {candidate.source}")

                        if candidate.snippet:
                            st.write(candidate.snippet)

                        st.info(
                            "Availability has not been confirmed. "
                            "Verify directly with the provider."
                        )

                        if candidate.url:
                            st.link_button(
                                "View source",
                                candidate.url,
                                use_container_width=True,
                            )

            else:
                st.warning(
                    "The search was performed, but no usable resource "
                    "candidates were returned."
                )

    else:
        st.warning(
            "Resource discovery results are not available in the workflow state."
        )

    st.divider()

    st.markdown(
        '<div class="section-label">07 / Recovery planning</div>',
        unsafe_allow_html=True,
    )

    st.markdown("### Recovery strategies")

    recovery_plan = result.get("recovery_plan")

    if recovery_plan:
        for index, strategy in enumerate(
            recovery_plan.strategies,
            start=1,
        ):
            with st.expander(
                f"Strategy {index}: {strategy.name}",
                expanded=index == 1,
            ):
                st.write(strategy.description)

                st.markdown("**Affected tasks**")
                st.write(", ".join(strategy.affected_tasks))

                st.markdown("**Benefits**")

                for benefit in strategy.benefits:
                    st.write(f"- {benefit}")

                st.markdown("**Risks**")

                for risk in strategy.risks:
                    st.write(f"- {risk}")

                st.markdown("**Assumptions**")

                for assumption in strategy.assumptions:
                    st.write(f"- {assumption}")

        st.markdown("**Recommendation**")
        st.write(recovery_plan.recommendation)

    recovery_review = result.get("recovery_review")

    if recovery_review:
        st.divider()

        st.markdown(
            '<div class="section-label">08 / Strategy review</div>',
            unsafe_allow_html=True,
        )

        st.markdown("### Reviewer assessment")

        if recovery_review.approved:
            st.success("Recovery plan approved.")
        else:
            st.warning("Recovery plan was not approved.")

        st.write(recovery_review.overall_assessment)

        for review in recovery_review.strategy_reviews:
            with st.expander(review.strategy_name):
                st.write(
                    "**Status:** "
                    + ("Acceptable" if review.is_acceptable else "Needs revision")
                )

                st.write(f"**Severity:** {review.severity}")

                if review.issues:
                    st.markdown("**Issues**")

                    for issue in review.issues:
                        st.write(f"- {issue}")

                if review.suggestions:
                    st.markdown("**Suggestions**")

                    for suggestion in review.suggestions:
                        st.write(f"- {suggestion}")

    execution_plan = result.get("execution_plan")

    if execution_plan:
        st.divider()

        st.markdown(
            '<div class="section-label">09 / Execution</div>',
            unsafe_allow_html=True,
        )

        st.markdown("### Recovery action plan")

        st.write(execution_plan.execution_summary)

        for step in execution_plan.action_steps:
            with st.container(border=True):
                st.markdown(f"**Step {step.step} — {step.priority.upper()}**")

                st.write(step.description)

                if step.related_tasks:
                    st.caption("Related tasks: " + ", ".join(step.related_tasks))

        st.markdown("### Stakeholder communications")

        for communication in execution_plan.stakeholder_communications:
            with st.expander(
                f"{communication.stakeholder_role} — {communication.communication_type}"
            ):
                st.caption(f"Urgency: {communication.urgency.upper()}")

                st.write(communication.message)

    execution_artifacts = result.get("execution_artifacts", {})

    if execution_artifacts:
        st.divider()

        st.markdown(
            '<div class="section-label">10 / Recovery artifacts</div>',
            unsafe_allow_html=True,
        )

        st.markdown("### Download artifacts")

        for artifact_name, artifact_path in execution_artifacts.items():
            path = Path(artifact_path)

            if not path.is_file():
                st.error(f"Artifact not found: {path}")
                continue

            mime_type = {
                ".pdf": "application/pdf",
                ".md": "text/markdown",
            }.get(
                path.suffix.lower(),
                "application/octet-stream",
            )

            st.download_button(
                label=f"Download {path.name}",
                data=path.read_bytes(),
                file_name=path.name,
                mime=mime_type,
                key=f"download_{artifact_name}",
                use_container_width=True,
            )
