from waymark.agents.analyst import analyze_disruption

PROJECT_CONTEXT = """
PROJECT: Tech Fest

A: Venue preparation
Duration: 2 days
Dependencies: None

B: Stage decoration
Duration: 2 days
Dependencies: A

C: Sound setup
Duration: 2 days
Dependencies: B

D: Lighting setup
Duration: 2 days
Dependencies: A

E: Final inspection
Duration: 1 day
Dependencies: C and D
"""


DISRUPTION_DESCRIPTION = """
Task B's start is delayed by exactly 2 calendar days.
Its duration remains unchanged.
"""


def main():
    result = analyze_disruption(
        disruption_description=DISRUPTION_DESCRIPTION,
        project_context=PROJECT_CONTEXT,
    )

    print("\nCHANGE ANALYST RESULT")
    print("=" * 50)
    print(result.model_dump_json(indent=2))

    assert result.task_id == "B"
    assert result.delay_days == 2
    assert result.reason.strip()

    print("\nAll analyst checks passed!")


if __name__ == "__main__":
    main()
