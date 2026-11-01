from datetime import date

from waymark.agents.reviewer import review_recovery_plan
from waymark.schemas.plan import ProjectPlan
from waymark.schemas.recovery import RecoveryPlan
from waymark.schemas.review import RecoveryReview

plan = ProjectPlan(
    id="tech-fest",
    name="Tech Fest",
    start_date=date(2026, 12, 1),
    deadline=date(2026, 12, 10),
    tasks=[
        {
            "id": "A",
            "name": "Venue preparation",
            "duration_days": 2,
            "dependencies": [],
        },
        {
            "id": "B",
            "name": "Stage decoration",
            "duration_days": 2,
            "dependencies": ["A"],
        },
        {
            "id": "C",
            "name": "Sound setup",
            "duration_days": 2,
            "dependencies": ["B"],
        },
        {
            "id": "D",
            "name": "Lighting setup",
            "duration_days": 2,
            "dependencies": ["A"],
        },
        {
            "id": "E",
            "name": "Final inspection",
            "duration_days": 1,
            "dependencies": ["C", "D"],
        },
    ],
)


recovery_plan = RecoveryPlan(
    strategies=[
        {
            "name": "Enhanced Monitoring",
            "description": (
                "Monitor tasks B, C and E daily to prevent further delays."
            ),
            "affected_tasks": ["B", "C", "E"],
            "benefits": ["Early identification of issues"],
            "risks": ["Additional coordination effort"],
            "assumptions": [],
        },
        {
            "name": "Resource Verification",
            "description": (
                "Verify the availability of required resources before tasks C and E."
            ),
            "affected_tasks": ["C", "E"],
            "benefits": ["Prevents resource-related delays"],
            "risks": ["Resources may not be available"],
            "assumptions": ["Required resources are available."],
        },
    ],
    recommendation=("Implement both strategies to reduce the risk of further delays."),
)


def main():
    result = review_recovery_plan(
        recovery_plan=recovery_plan,
        plan=plan,
        affected_tasks={"B", "C", "E"},
        validation_errors=[],
    )

    assert isinstance(result, RecoveryReview)

    assert len(result.strategy_reviews) == 2

    for review in result.strategy_reviews:
        assert review.strategy_name.strip()
        assert isinstance(review.is_acceptable, bool)

    assert result.overall_assessment.strip()

    print("\nCONSTRAINT REVIEW:")
    print(result.model_dump_json(indent=2))

    print("\nREVIEW SUMMARY:")

    for review in result.strategy_reviews:
        print(f"\nStrategy: {review.strategy_name}")
        print("Acceptable:", review.is_acceptable)
        print("Issues:", review.issues)
        print("Suggestions:", review.suggestions)

    print("\nOverall approved:", result.approved)

    print("\nALL REVIEWER CHECKS PASSED!")


if __name__ == "__main__":
    main()
