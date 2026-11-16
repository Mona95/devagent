import os
import requests
from dotenv import load_dotenv

load_dotenv()

def web_search(query: str) -> str:
    """
    Search the internet using SerpAPI.
    Returns top search results as formatted text.
    """
    api_key = os.getenv("SERPAPI_KEY")

    if not api_key:
        return "Error: SERPAPI_KEY not set"

    try:
        params = {
            "q": query,
            "api_key": api_key,
            "num": 5,
            "engine": "google"
        }

        response = requests.get(
            "https://serpapi.com/search",
            params=params,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        results = []

        # Organic results
        for result in data.get("organic_results", [])[:5]:
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            link = result.get("link", "")
            results.append(f"**{title}**\n{snippet}\n{link}")

        if not results:
            return "No results found"

        return "\n\n".join(results)

    except Exception as e:
        return f"Search failed: {str(e)}"