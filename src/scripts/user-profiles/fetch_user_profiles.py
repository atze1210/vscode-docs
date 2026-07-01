import requests
import os
import time
import json

# GitHub API URL for VS Code docs contributors
GITHUB_API_URL = "https://api.github.com/repos/microsoft/vscode-docs/contributors"

# Data folder and output file paths
DATA_FOLDER = "data/user-profiles"
os.makedirs(DATA_FOLDER, exist_ok=True)
OUTPUT_FILE = os.path.join(DATA_FOLDER, "user_profiles.json")

# HTTP headers
HEADERS = {
    "User-Agent": "vscode-docs/1.0",
    "Accept": "application/vnd.github+json",
}

# Add token if available
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"

# Rate limit configuration — target rate to stay within GitHub's secondary rate limits
REQUESTS_PER_SECOND = 1
SLEEP_TIME = 1 / REQUESTS_PER_SECOND


REQUEST_TIMEOUT = 30


def fetch_contributors(api_url, headers):
    """Fetch all contributors from the GitHub API with pagination."""
    contributors = []
    page = 1
    while True:
        try:
            response = requests.get(
                api_url,
                headers=headers,
                params={"per_page": 100, "page": page},
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise requests.HTTPError(
                f"Failed to fetch contributors page {page}: {exc}"
            ) from exc
        page_data = response.json()
        if not page_data:
            break
        contributors.extend(page_data)
        page += 1
        time.sleep(SLEEP_TIME)
    return contributors


def fetch_user_details(username, headers):
    """Fetch detailed profile information for a GitHub user."""
    response = requests.get(
        f"https://api.github.com/users/{username}",
        headers=headers,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    time.sleep(SLEEP_TIME)
    return response.json()


def build_profile(contributor, details):
    """Build a user profile record from contributor and user details."""
    return {
        "login": contributor.get("login", "").strip(),
        "id": contributor.get("id"),
        "avatar_url": contributor.get("avatar_url", "").strip(),
        "profile_url": contributor.get("html_url", "").strip(),
        "contributions": contributor.get("contributions", 0),
        "name": (details.get("name") or "").strip(),
        "email": (details.get("email") or "").strip(),
        "company": (details.get("company") or "").strip(),
        "blog": (details.get("blog") or "").strip(),
        "location": (details.get("location") or "").strip(),
        "bio": (details.get("bio") or "").strip(),
        "public_repos": details.get("public_repos", 0),
        "followers": details.get("followers", 0),
        "following": details.get("following", 0),
        "created_at": (details.get("created_at") or "").strip(),
        "updated_at": (details.get("updated_at") or "").strip(),
    }


def download_and_process_profiles(api_url, headers, output_file):
    """Fetch contributor profiles, process them, and save to JSON."""
    contributors = fetch_contributors(api_url, headers)

    profiles = []
    for contributor in contributors:
        login = contributor.get("login", "")
        if not login:
            continue
        try:
            details = fetch_user_details(login, headers)
        except requests.HTTPError as exc:
            print(f"Warning: failed to fetch details for '{login}': {exc}")
            details = {}
        profile = build_profile(contributor, details)
        profiles.append(profile)

    output_json = {
        "fields": [
            "login",
            "id",
            "avatar_url",
            "profile_url",
            "contributions",
            "name",
            "email",
            "company",
            "blog",
            "location",
            "bio",
            "public_repos",
            "followers",
            "following",
            "created_at",
            "updated_at",
        ],
        "data": profiles,
    }

    with open(output_file, "w") as file:
        json.dump(output_json, file, indent=4)
    print(f"Processed user profiles saved to {output_file}")


download_and_process_profiles(GITHUB_API_URL, HEADERS, OUTPUT_FILE)
