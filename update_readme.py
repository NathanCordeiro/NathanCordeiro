import os
import requests
import json
import re

github_token = os.getenv("GH_TOKEN")
wakatime_api_key = os.getenv("WAKATIME_API_KEY")
github_username = "NathanCordeiro"

print(f"Running update_readme.py for {github_username}")

if not github_token:
    print("❌ GH_TOKEN is missing!")
if not wakatime_api_key:
    print("❌ WAKATIME_API_KEY is missing!")

def fetch_github_stats():
    url = f"https://api.github.com/users/{github_username}"
    response = requests.get(url, headers={"Authorization": f"token {github_token}"})
    data = response.json()
    
    if response.status_code != 200:
        print(f"❌ GitHub API error: {data}")
    
    return {
        "public_repos": data.get("public_repos", 0),
        "private_repos": fetch_private_repos_count()
    }

def fetch_private_repos_count():
    url = "https://api.github.com/user/repos?visibility=private"
    response = requests.get(url, headers={"Authorization": f"token {github_token}"})
    repos = response.json()
    
    if response.status_code != 200:
        print(f"❌ GitHub API error: {repos}")
    
    return len(repos) if isinstance(repos, list) else 0

def fetch_wakatime_stats():
    url = "https://wakatime.com/api/v1/users/current/stats/last_7_days"
    response = requests.get(url, headers={"Authorization": f"Bearer {wakatime_api_key}"})
    
    if response.status_code != 200:
        print("❌ WakaTime API error:", response.text)
    
    return response.json() if response.status_code == 200 else {}

def update_readme():
    print("📖 Reading README.md...")
    
    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()

    github_stats = fetch_github_stats()
    wakatime_stats = fetch_wakatime_stats()

    print(f"📜 Public Repos: {github_stats['public_repos']}, Private Repos: {github_stats['private_repos']}")

    readme = re.sub(r"> 📜 \d+ Public Repositories", f"> 📜 {github_stats['public_repos']} Public Repositories", readme)
    readme = re.sub(r"> 🔑 \d+ Private Repositories", f"> 🔑 {github_stats['private_repos']} Private Repositories", readme)
    
    if wakatime_stats:
        last_updated = wakatime_stats.get("data", {}).get("start", "Unknown")
        readme = re.sub(r"Last Updated on .*? UTC", f"Last Updated on {last_updated} UTC", readme)

    print("📝 Writing updated README.md...")

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)

    print("✅ README.md update complete!")

if __name__ == "__main__":
    update_readme()
