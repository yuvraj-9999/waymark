from pydantic import BaseModel, Field

from waymark.config import settings
from waymark.llm.gemini_client import client
from waymark.schemas.plan import ProjectPlan
from waymark.schemas.recovery import RecoveryPlan
from waymark.schemas.review import RecoveryReview, StrategyReview


class GeminiStrategyReview(BaseModel):
    strategy_name: str
    is_acceptable: bool
    issues: list[str]
    suggestions: list[str]
    severity: str = Field(
        default="none",
        pattern="^(none|warning|blocking)$",
    )


class GeminiRecoveryReview(BaseModel):
    strategy_reviews: list[GeminiStrategyReview]
    overall_assessment: str
    approved: bool


def validate_recovery_plan(
    recovery_plan: RecoveryPlan,
    plan: ProjectPlan,
    affected_tasks: set[str],
    validation_errors: list[str],
) -> list[StrategyReview]:
    """Deterministically check recovery strategies against project constraints."""

    known_task_ids = {task.id for task in plan.tasks}
    reviews = []

    for strategy in recovery_plan.strategies:
        issues = []
        suggestions = []

        unknown_tasks = set(strategy.affected_tasks) - known_task_ids

        if unknown_tasks:
            issues.append(f"Unknown task IDs: {sorted(unknown_tasks)}")

        unrelated_tasks = set(strategy.affected_tasks) - affected_tasks

        if unrelated_tasks:
            issues.append(
                f"Tasks not identified as affected: {sorted(unrelated_tasks)}"
            )

        if validation_errors:
            issues.extend(validation_errors)

        reviews.append(
            StrategyReview(
                strategy_name=strategy.name,
                is_acceptable=not issues,
                issues=issues,
                suggestions=suggestions,
                severity="blocking" if issues else "none",
            )
        )

    return reviews


def review_recovery_plan(
    recovery_plan: RecoveryPlan,
    plan: ProjectPlan,
    affected_tasks: set[str],
    validation_errors: list[str],
) -> RecoveryReview:
    """Review recovery strategies using Gemini and deterministic checks."""

    deterministic_reviews = validate_recovery_plan(
        recovery_plan=recovery_plan,
        plan=plan,
        affected_tasks=affected_tasks,
        validation_errors=validation_errors,
    )

    strategy_names = [strategy.name for strategy in recovery_plan.strategies]

    if len(strategy_names) != len(set(strategy_names)):
        raise ValueError("Recovery strategies must have unique names.")

    prompt = f"""
    You are Waymark's Constraint Reviewer.

    Independently evaluate the proposed recovery strategies.

    PROJECT PLAN:
    {plan.model_dump_json(indent=2)}

    RECOVERY PLAN:
    {recovery_plan.model_dump_json(indent=2)}

    DETERMINISTIC REVIEW RESULTS:
    {[review.model_dump() for review in deterministic_reviews]}

    VALIDATION ERRORS:
    {validation_errors}

    REVIEW RULES:

    1. Evaluate every recovery strategy independently.
    2. Do not approve strategies with deterministic issues.
    3. Do not recommend changing task durations or dependencies.
    4. Do not assume additional resources are available.
    5. Flag unverified resource availability claims.
    6. Do not claim critical-path analysis has been performed.
    7. Distinguish verified facts from assumptions.
    8. Identify unsupported claims and unrealistic proposals.
    9. Provide practical suggestions to address identified issues.
    10. Even when a strategy has no identified issues, suggest
        ways to improve its effectiveness where appropriate.
    11. Suggestions should be actionable, specific, and relevant
        to the affected tasks.
    12. Do not generate unnecessary suggestions merely to
        populate the suggestions list.
    13. Approve the overall recovery plan only if:
        - Every proposed strategy has been reviewed.
        - Every strategy is acceptable.
        - No strategy has blocking severity.
        - Deterministic schedule validation passes.

    Return a structured review.
    """

    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": GeminiRecoveryReview,
            "temperature": 0.1,
        },
    )

    if not response.text:
        raise ValueError("Gemini returned an empty recovery review.")

    gemini_review = GeminiRecoveryReview.model_validate_json(response.text)

    ai_review = RecoveryReview.model_validate(gemini_review.model_dump())

    expected_names = set(strategy_names)

    returned_names = [review.strategy_name for review in ai_review.strategy_reviews]

    if (
        len(returned_names) != len(expected_names)
        or set(returned_names) != expected_names
    ):
        raise ValueError("Reviewer must return exactly one review for every strategy.")

    deterministic_by_name = {
        review.strategy_name: review for review in deterministic_reviews
    }

    final_reviews = []

    for ai_strategy in ai_review.strategy_reviews:
        deterministic = deterministic_by_name.get(ai_strategy.strategy_name)

        if deterministic is None:
            raise ValueError(
                f"Reviewer returned an unknown strategy: {ai_strategy.strategy_name}"
            )

        issues = list(dict.fromkeys(ai_strategy.issues + deterministic.issues))

        if deterministic.severity == "blocking":
            severity = "blocking"
        else:
            severity = ai_strategy.severity

            if issues and severity == "none":
                severity = "warning"

        final_reviews.append(
            StrategyReview(
                strategy_name=ai_strategy.strategy_name,
                is_acceptable=(
                    ai_strategy.is_acceptable
                    and deterministic.is_acceptable
                    and severity != "blocking"
                ),
                issues=list(dict.fromkeys(issues)),
                suggestions=ai_strategy.suggestions,
                severity=severity,
            )
        )

    all_acceptable = (
        len(final_reviews) == len(recovery_plan.strategies)
        and all(
            review.is_acceptable and review.severity != "blocking"
            for review in final_reviews
        )
        and not validation_errors
    )

    return RecoveryReview(
        strategy_reviews=final_reviews,
        overall_assessment=ai_review.overall_assessment,
        approved=ai_review.approved and all_acceptable,
    )
