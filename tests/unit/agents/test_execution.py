from datetime import date

from waymark.artifacts.recovery_report import generate_recovery_report
from waymark.schemas.disruption import Disruption
from waymark.schemas.plan import ProjectPlan
from waymark.schemas.recovery import RecoveryPlan, RecoveryStrategy
from waymark.schemas.review import RecoveryReview, StrategyReview
from waymark.schemas.schedule import Schedule, ScheduledTask
from waymark.schemas.task import Task


def test_generate_recovery_report_creates_pdf(tmp_path):
    plan = ProjectPlan(
        id="project-1",
        name="Event Preparation",
        start_date=date(2026, 12, 1),
        deadline=date(2026, 12, 20),
        tasks=[
            Task(
                id="A",
                name="Venue Booking",
                duration_days=2,
                dependencies=[],
            ),
            Task(
                id="B",
                name="Decoration",
                duration_days=2,
                dependencies=["A"],
            ),
        ],
    )

    disruption = Disruption(
        task_id="B",
        delay_days=2,
        reason="Decoration materials are delayed.",
    )

    original_schedule = Schedule(
        tasks=[
            ScheduledTask(
                task_id="A",
                start_date=date(2026, 12, 1),
                finish_date=date(2026, 12, 3),
            ),
            ScheduledTask(
                task_id="B",
                start_date=date(2026, 12, 3),
                finish_date=date(2026, 12, 5),
            ),
        ]
    )

    revised_schedule = Schedule(
        tasks=[
            ScheduledTask(
                task_id="A",
                start_date=date(2026, 12, 1),
                finish_date=date(2026, 12, 3),
            ),
            ScheduledTask(
                task_id="B",
                start_date=date(2026, 12, 5),
                finish_date=date(2026, 12, 7),
            ),
        ]
    )

    recovery_plan = RecoveryPlan(
        strategies=[
            RecoveryStrategy(
                name="Reorganize preparation",
                description="Adjust preparation activities.",
                affected_tasks=["B"],
                benefits=["Improved coordination"],
                risks=["Additional coordination required"],
                assumptions=["Task duration remains unchanged"],
            )
        ],
        recommendation="Use the revised schedule.",
    )

    recovery_review = RecoveryReview(
        strategy_reviews=[
            StrategyReview(
                strategy_name="Reorganize preparation",
                is_acceptable=True,
                issues=[],
                suggestions=[],
                severity="none",
            )
        ],
        overall_assessment="The recovery strategy is acceptable.",
        approved=True,
    )

    output_path = generate_recovery_report(
        plan=plan,
        disruption=disruption,
        affected_tasks=["B"],
        original_schedule=original_schedule,
        revised_schedule=revised_schedule,
        recovery_plan=recovery_plan,
        recovery_review=recovery_review,
        output_dir=tmp_path,
    )

    pdf_file = tmp_path / "recovery_report.pdf"

    assert pdf_file.exists()
    assert pdf_file.stat().st_size > 0
    assert output_path == str(pdf_file)

    with pdf_file.open("rb") as file:
        assert file.read(5) == b"%PDF-"
