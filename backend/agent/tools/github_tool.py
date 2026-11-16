import os
import requests
from dotenv import load_dotenv

load_dotenv()

def github_repo(repo: str) -> str:
    """
    Fetch information about a GitHub repository.
    Input format: "owner/repo" or full GitHub URL
    """
    try:
        # Handle full URLs
        if "github.com" in repo:
            parts = repo.replace("https://", "").replace("http://", "")
            parts = parts.replace("github.com/", "").strip("/")
            repo = "/".join(parts.split("/")[:2])

        token = os.getenv("GITHUB_TOKEN")
        headers = {"Accept": "application/vnd.github.v3+json"}
        if token:
            headers["Authorization"] = f"token {token}"

        base_url = f"https://api.github.com/repos/{repo}"

        # Get repo info
        response = requests.get(base_url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        result = f"""Repository: {data.get('full_name')}
Description: {data.get('description', 'No description')}
Language: {data.get('language', 'Unknown')}
Stars: {data.get('stargazers_count', 0)}
Forks: {data.get('forks_count', 0)}
Open Issues: {data.get('open_issues_count', 0)}
Created: {data.get('created_at', '')}
Last Updated: {data.get('updated_at', '')}
URL: {data.get('html_url', '')}"""

        # Get README
        readme_response = requests.get(
            f"{base_url}/readme",
            headers={**headers, "Accept": "application/vnd.github.raw"},
            timeout=10
        )
        if readme_response.status_code == 200:
            readme = readme_response.text[:2000]
            result += f"\n\nREADME (first 2000 chars):\n{readme}"

        # Get top files
        contents_response = requests.get(
            f"{base_url}/contents",
            headers=headers,
            timeout=10
        )
        if contents_response.status_code == 200:
            files = [f['name'] for f in contents_response.json()
                    if isinstance(f, dict)]
            result += f"\n\nRoot files: {', '.join(files[:20])}"

        return result

    except Exception as e:
        return f"Failed to fetch repo: {str(e)}"