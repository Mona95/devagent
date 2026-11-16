import httpx
from bs4 import BeautifulSoup

def read_url(url: str) -> str:
    """
    Fetch and extract readable text from a webpage.
    Removes HTML tags, scripts, and styling.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; DevAgent/1.0)"
        }

        with httpx.Client(timeout=15, follow_redirects=True) as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove scripts, styles, nav elements
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        # Get clean text
        text = soup.get_text(separator="\n", strip=True)

        # Remove excessive blank lines
        lines = [line for line in text.splitlines() if line.strip()]
        clean_text = "\n".join(lines)

        # Limit to 3000 chars to avoid token overflow
        if len(clean_text) > 3000:
            clean_text = clean_text[:3000] + "\n\n[Content truncated...]"

        return clean_text

    except Exception as e:
        return f"Failed to read URL: {str(e)}"