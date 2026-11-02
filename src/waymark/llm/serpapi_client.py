"""Client for performing live Google search through SerpApi"""

import httpx

from waymark.config import settings

SERPAPI_URL = "https://serpapi.com/search.json"


def search_web(
    query: str,
    location: str | None = None,
    num_results: int = 5,
) -> list[dict]:
    """Search the web and return organic results."""

    params = {
        "engine": "google",
        "q": query,
        "api_key": settings.serpapi_api_key,
        "num": num_results,
    }

    if location:
        params["location"] = location

    try:
        response = httpx.get(SERPAPI_URL, params=params, timeout=20.0)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise RuntimeError(f"SerpApi request failed: {exc}") from exc

    data = response.json()

    if "error" in data:
        raise RuntimeError(f"SerpApi error: {data['error']}")

    organic_results = data.get("organic_results", [])

    return organic_results
