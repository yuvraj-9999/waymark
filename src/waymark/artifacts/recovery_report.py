from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from waymark.schemas.disruption import Disruption
from waymark.schemas.plan import ProjectPlan
from waymark.schemas.recovery import RecoveryPlan
from waymark.schemas.resource_scout import ResourceScoutResult
from waymark.schemas.review import RecoveryReview
from waymark.schemas.schedule import Schedule


def generate_recovery_report(
    plan: ProjectPlan,
    disruption: Disruption,
    affected_tasks: list[str],
    original_schedule: Schedule,
    revised_schedule: Schedule,
    recovery_plan: RecoveryPlan,
    recovery_review: RecoveryReview,
    resource_scout_result: ResourceScoutResult | None = None,
    output_dir: Path = Path("artifacts"),
) -> str:
    """Generate a PDF recovery report and return its file path."""

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "recovery_report.pdf"

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "WaymarkTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1D3557"),
        spaceAfter=20,
    )

    heading_style = ParagraphStyle(
        "WaymarkHeading",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#1D3557"),
        spaceBefore=12,
        spaceAfter=8,
    )

    body_style = styles["BodyText"]
    story = []

    story.append(Paragraph("Waymark Recovery Report", title_style))
    story.append(Paragraph(f"<b>Project:</b> {escape(plan.name)}", body_style))
    story.append(Paragraph(f"<b>Project ID:</b> {escape(plan.id)}", body_style))
    story.append(
        Paragraph(
            f"<b>Deadline:</b> {plan.deadline.isoformat()}",
            body_style,
        )
    )
    story.append(Spacer(1, 12))

    story.append(Paragraph("1. Disruption Details", heading_style))
    story.append(
        Paragraph(
            f"<b>Task:</b> {escape(disruption.task_id)}",
            body_style,
        )
    )
    story.append(
        Paragraph(
            f"<b>Delay:</b> {disruption.delay_days} day(s)",
            body_style,
        )
    )
    story.append(
        Paragraph(
            f"<b>Reason:</b> {escape(disruption.reason)}",
            body_style,
        )
    )

    story.append(Paragraph("2. Impact Analysis", heading_style))

    task_names = {task.id: task.name for task in plan.tasks}

    if affected_tasks:
        for task_id in affected_tasks:
            task_name = task_names.get(task_id, "Unknown task")
            story.append(
                Paragraph(
                    f"• {escape(task_id)} — {escape(task_name)}",
                    body_style,
                )
            )
    else:
        story.append(Paragraph("No affected tasks.", body_style))

    story.append(Paragraph("3. Schedule Comparison", heading_style))

    original_dates = {task.task_id: task for task in original_schedule.tasks}
    revised_dates = {task.task_id: task for task in revised_schedule.tasks}

    table_data = [
        [
            "Task",
            "Name",
            "Original Start",
            "Original Finish",
            "Revised Start",
            "Revised Finish",
        ]
    ]

    for task_id, revised_task in revised_dates.items():
        original_task = original_dates.get(task_id)

        table_data.append(
            [
                task_id,
                task_names.get(task_id, "Unknown"),
                original_task.start_date.isoformat() if original_task else "N/A",
                original_task.finish_date.isoformat() if original_task else "N/A",
                revised_task.start_date.isoformat(),
                revised_task.finish_date.isoformat(),
            ]
        )

    schedule_table = Table(
        table_data,
        repeatRows=1,
        colWidths=[
            0.5 * inch,
            1.2 * inch,
            1.0 * inch,
            1.0 * inch,
            1.0 * inch,
            1.0 * inch,
        ],
    )

    schedule_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#1D3557"),
                ),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    story.append(schedule_table)

    story.append(Paragraph("4. Recovery Strategies", heading_style))

    for index, strategy in enumerate(
        recovery_plan.strategies,
        start=1,
    ):
        story.append(
            Paragraph(
                f"<b>{index}. {escape(strategy.name)}</b>",
                body_style,
            )
        )
        story.append(
            Paragraph(
                escape(strategy.description),
                body_style,
            )
        )

        if strategy.affected_tasks:
            story.append(
                Paragraph(
                    "<b>Affected tasks:</b> "
                    + ", ".join(escape(task) for task in strategy.affected_tasks),
                    body_style,
                )
            )

        if strategy.benefits:
            story.append(
                Paragraph(
                    "<b>Benefits:</b> "
                    + "; ".join(escape(item) for item in strategy.benefits),
                    body_style,
                )
            )

        if strategy.risks:
            story.append(
                Paragraph(
                    "<b>Risks:</b> "
                    + "; ".join(escape(item) for item in strategy.risks),
                    body_style,
                )
            )

        story.append(Spacer(1, 8))

    story.append(
        Paragraph(
            f"<b>Recommendation:</b> {escape(recovery_plan.recommendation)}",
            body_style,
        )
    )

    story.append(Paragraph("5. Resource Discovery", heading_style))

    if resource_scout_result is None:
        story.append(
            Paragraph(
                "Resource discovery information was not provided.",
                body_style,
            )
        )

    elif not resource_scout_result.search_performed:
        story.append(
            Paragraph(
                escape(resource_scout_result.explanation),
                body_style,
            )
        )

    else:
        story.append(
            Paragraph(
                f"<b>Search query:</b> {escape(resource_scout_result.search_query)}",
                body_style,
            )
        )

        story.append(
            Paragraph(
                escape(resource_scout_result.explanation),
                body_style,
            )
        )

        if resource_scout_result.candidates:
            for index, candidate in enumerate(
                resource_scout_result.candidates,
                start=1,
            ):
                story.append(
                    Paragraph(
                        f"<b>{index}. {escape(candidate.title)}</b>",
                        body_style,
                    )
                )

                if candidate.source:
                    story.append(
                        Paragraph(
                            f"<b>Source:</b> {escape(candidate.source)}",
                            body_style,
                        )
                    )

                if candidate.snippet:
                    story.append(
                        Paragraph(
                            escape(candidate.snippet),
                            body_style,
                        )
                    )

                if candidate.url:
                    safe_url = escape(
                        candidate.url,
                        {
                            '"': "&quot;",
                            "'": "&apos;",
                        },
                    )

                    story.append(
                        Paragraph(
                            f'<link href="{safe_url}" '
                            f'color="#1D3557">Open source</link>',
                            body_style,
                        )
                    )

                availability_status = (
                    "Confirmed" if candidate.availability_confirmed else "Not confirmed"
                )

                story.append(
                    Paragraph(
                        f"<b>Availability:</b> {availability_status}",
                        body_style,
                    )
                )

                story.append(Spacer(1, 8))

        else:
            story.append(
                Paragraph(
                    "The search was performed, but no usable candidates were returned.",
                    body_style,
                )
            )

    story.append(Paragraph("6. Reviewer Assessment", heading_style))

    approval_status = "Approved" if recovery_review.approved else "Rejected"

    story.append(
        Paragraph(
            f"<b>Approval status:</b> {approval_status}",
            body_style,
        )
    )

    story.append(
        Paragraph(
            escape(recovery_review.overall_assessment),
            body_style,
        )
    )

    for review in recovery_review.strategy_reviews:
        status = "Acceptable" if review.is_acceptable else "Not acceptable"

        story.append(
            Paragraph(
                f"<b>{escape(review.strategy_name)}:</b> "
                f"{status} — Severity: {escape(review.severity)}",
                body_style,
            )
        )

        if review.issues:
            story.append(
                Paragraph(
                    "<b>Issues:</b> "
                    + "; ".join(escape(issue) for issue in review.issues),
                    body_style,
                )
            )

        if review.suggestions:
            story.append(
                Paragraph(
                    "<b>Suggestions:</b> "
                    + "; ".join(
                        escape(suggestion) for suggestion in review.suggestions
                    ),
                    body_style,
                )
            )

    document.build(story)

    return str(output_path)
