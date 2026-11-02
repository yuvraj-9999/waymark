from waymark.llm.serpapi_client import search_web


def main():
    results = search_web(
        query="auditoriums for college events in Nashik",
        location="Nashik, Maharashtra, India",
        num_results=5,
    )

    print(f"Found {len(results)} results\n")

    for index, result in enumerate(results, start=1):
        print(f"Result {index}")
        print("Title:", result.get("title"))
        print("URL:", result.get("link"))
        print("Snippet:", result.get("snippet"))
        print("-" * 60)


if __name__ == "__main__":
    main()
