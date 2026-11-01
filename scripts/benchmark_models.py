from google.genai.errors import APIError

from waymark.llm.benchmark import BenchmarkError, run_benchmark

PROMPT = """
Analyze the following project disruption.

PROJECT START: December 1, 2026
PROJECT DEADLINE: December 10, 2026

BASELINE SCHEDULE:

A: Venue preparation
Duration: 2 days
Start: December 1
Finish: December 3
Dependencies: None
Resource: Venue team

B: Stage decoration
Duration: 2 days
Start: December 3
Finish: December 5
Dependencies: A
Resource: Decoration team

C: Sound setup
Duration: 2 days
Start: December 5
Finish: December 7
Dependencies: B
Resource: Equipment X

D: Lighting setup
Duration: 2 days
Start: December 3
Finish: December 5
Dependencies: A
Resource: Equipment X

E: Final inspection
Duration: 1 day
Start: December 7
Finish: December 8
Dependencies: C and D
Resource: Inspection team

Equipment X is used sequentially:
D uses it first, followed by C.

DISRUPTION:

1. Task B's START is delayed by exactly 2 calendar days.
2. B's duration remains 2 days.
3. The original decoration team is unavailable.
4. A replacement decoration team may be available, but this is unconfirmed.
5. C and D require exclusive access to Equipment X.
6. The project deadline cannot be extended.

RULES:

- Do not interpret the delay as an increase in task duration.
- Do not assume the replacement team is available.
- Do not change task durations.
- Do not relax dependencies.
- Do not schedule C and D simultaneously.
- Do not invent resources.
- Distinguish confirmed facts from unknown information.
- Do not claim deadline feasibility without establishing it.

Return ONLY a JSON object with these exact keys:

{
  "directly_affected": [],
  "indirectly_affected": [],
  "unaffected": [],
  "explanation": "Your concise explanation"
}

All three task fields must contain arrays of task IDs.
The explanation must describe the impact and uncertainties.
"""


def main():
    print("\n" + "=" * 70)
    print("WAYMARK - GEMINI BENCHMARK")
    print("=" * 70)

    try:
        result = run_benchmark(PROMPT)

        print("\nRESPONSE:")
        print(result["analysis"].model_dump_json(indent=2))

        print(f"\nModel: {result['model']}")
        print(f"Latency: {result['latency_seconds']} seconds")
        print(f"Tokens: {result['tokens_used']}")

    except (BenchmarkError, APIError) as error:
        print(f"\nBENCHMARK FAILED: {error}")


if __name__ == "__main__":
    main()
