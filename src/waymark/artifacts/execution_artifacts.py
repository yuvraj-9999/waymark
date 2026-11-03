
from pathlib import Path

from waymark.artifacts.recovery_report import generate_recovery_report
from waymark.schemas.disruption import Disruption
from waymark.schemas.execution import ExecutionPlan
from waymark.schemas.plan import ProjectPlan
from waymark.schemas.recovery import RecoveryPlan
from waymark.schemas.resource_scout import ResourceScoutResult
from waymark.schemas.review import RecoveryReview
from waymark.schemas.schedule import Schedule


def generate_execution_artifacts(
    plan: ProjectPlan,
    disruption: Disruption,
    affected_tasks: list[str],
    original_schedule: Schedule,
    revised_schedule: Schedule,
    recovery_plan: RecoveryPlan,
    recovery_review: RecoveryReview,
    execution_plan: ExecutionPlan,
    resource_scout_result: ResourceScoutResult | None = None,
    output_dir: Path = Path("artifacts"),
) -> dict[str, str]:
    """Generate recovery report, execution checklist, and communication drafts."""

    if not recovery_review.approved:
        raise ValueError(
            "Cannot generate execution artifacts for an unapproved recovery plan."
        )

    output_dir.mkdir(parents=True, exist_ok=True)

    recovery_report_path = generate_recovery_report(
        plan=plan,
        disruption=disruption,
        affected_tasks=affected_tasks,
        original_schedule=original_schedule,
        revised_schedule=revised_schedule,
        recovery_plan=recovery_plan,
        recovery_review=recovery_review,
        resource_scout_result=resource_scout_result,
        output_dir=output_dir,
    )

    checklist_path = output_dir / "execution_checklist.md"

    checklist_content = [
        f"# Execution Checklist — {plan.name}",
        "",
        f"**Disruption:** {disruption.reason}",
        "",
        "**Status:** Proposed actions — not yet completed",
        "",
        "## Action Steps",
        "",
    ]

    for step in execution_plan.action_steps:
        tasks = ", ".join(step.related_tasks) or "No specific tasks"

        checklist_content.extend(
            [
                f"- [ ] **Step {step.step} — {step.priority.upper()}**",
                f"  - {step.description}",
                f"  - Related tasks: {tasks}",
                "",
            ]
        )

    checklist_path.write_text(
        "\n".join(checklist_content),
        encoding="utf-8",
    )

    communications_path = output_dir / "stakeholder_communications.md"

    communications_content = [
        f"# Stakeholder Communications — {plan.name}",
        "",
        "**These are drafts. Review before sending.**",
        "",
    ]

    for index, communication in enumerate(
        execution_plan.stakeholder_communications,
        start=1,
    ):
        communications_content.extend(
            [
                f"## Communication {index}",
                "",
                f"**Stakeholder:** {communication.stakeholder_role}",
                f"**Type:** {communication.communication_type}",
                f"**Urgency:** {communication.urgency.upper()}",
                "",
                "### Draft",
                "",
                communication.message,
                "",
                "---",
                "",
            ]
        )

    communications_path.write_text(
        "\n".join(communications_content),
        encoding="utf-8",
    )

    return {
        "recovery_report": recovery_report_path,
        "execution_checklist": str(checklist_path),
        "stakeholder_communications": str(communications_path),
    }
