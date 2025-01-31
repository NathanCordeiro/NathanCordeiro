import os
import requests
import json
import re

github_token = os.getenv("GH_TOKEN")
wakatime_api_key = os.getenv("WAKATIME_API_KEY")
github_username = "YOUR_GITHUB_USERNAME"  # Replace with your GitHub username

GITHUB_HEADERS = {
    "Authorization": f"token {github_token}",
    "Accept": "application/vnd.github.v3+json"
}

def fetch_github_stats():
    url = f"https://api.github.com/users/{github_username}"
    response = requests.get(url, headers=GITHUB_HEADERS)
    data = response.json()
    return {
        "public_repos": data.get("public_repos", 0),
        "private_repos": fetch_private_repos_count(),
        "storage": "28.5 kB"  # GitHub API doesn’t provide this directly
    }

def fetch_private_repos_count():
    url = "https://api.github.com/user/repos?visibility=private"
    response = requests.get(url, headers=GITHUB_HEADERS)
    repos = response.json()
    return len(repos) if isinstance(repos, list) else 0

def fetch_wakatime_stats():
    url = "https://wakatime.com/api/v1/users/current/stats/last_7_days"
    response = requests.get(url, headers={"Authorization": f"Bearer {wakatime_api_key}"})
    if response.status_code == 200:
        return response.json()
    return {}

def update_readme():
    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()

    github_stats = fetch_github_stats()
    wakatime_stats = fetch_wakatime_stats()
    
    readme = re.sub(r"> 📜 \d+ Public Repositories", f"> 📜 {github_stats['public_repos']} Public Repositories", readme)
    readme = re.sub(r"> 🔑 \d+ Private Repositories", f"> 🔑 {github_stats['private_repos']} Private Repositories", readme)
    
    if wakatime_stats:
        last_updated = wakatime_stats.get("data", {}).get("start", "Unknown")
        readme = re.sub(r"Last Updated on .*? UTC", f"Last Updated on {last_updated} UTC", readme)
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)

if __name__ == "__main__":
    update_readme()
