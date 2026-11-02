from waymark.agents.resource_scout import scout_resources


def main():
    project_context = """
    Project: College Tech Fest
    Location: Nashik, Maharashtra, India
    Tasks:
    A - Book auditorium
    B - Arrange sound equipment
    C - Conduct event
    """

    disruption = (
        "Task B is delayed by 2 days because preparation is taking longer "
        "than expected. No resources are unavailable."
    )

    result = scout_resources(
        disruption_description=disruption,
        project_context=project_context,
    )

    print("Search performed:", result.search_performed)
    print("Search query:", result.search_query)
    print("Explanation:", result.explanation)

    for index, candidate in enumerate(result.candidates, start=1):
        print(f"\nCandidate {index}")
        print("Title:", candidate.title)
        print("URL:", candidate.url)
        print("Snippet:", candidate.snippet)
        print("Availability confirmed:", candidate.availability_confirmed)


if __name__ == "__main__":
    main()
