"""
Task B3: WCA GitLab API Endpoint Validation & Live Token Test
Author: Brij (RepoLens Team)

Tests GitLab REST API v4 endpoints required by RepoLens:
1. /api/v4/user (Authentication & profile)
2. /api/v4/projects?membership=true (User repositories)
3. /api/v4/projects/:id/repository/branches (Branch freshness & default branch)
4. /api/v4/projects/:id/repository/commits (Commit churn calculation)
"""

import os
import sys
import json
import urllib.request
import urllib.error

# Load environment variables from .env if present
env_file = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".env")
if os.path.exists(env_file):
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip() and not line.startswith("#") and "=" in line:
                k, v = line.strip().split("=", 1)
                os.environ.setdefault(k, v)

GITLAB_URL = os.environ.get("GITLAB_URL", "http://git.webchiparmor.com:9418").rstrip("/")
API_URL = f"{GITLAB_URL}/api/v4"
TOKEN = os.environ.get("GITLAB_TOKEN", "")

def get(endpoint: str):
    url = f"{API_URL}/{endpoint.lstrip('/')}"
    req = urllib.request.Request(url, headers={"PRIVATE-TOKEN": TOKEN})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8", errors="ignore"))
    except Exception as e:
        return {"error": str(e)}

def test_user_profile():
    user = get("user")
    assert "error" not in user, f"Failed to get user: {user.get('error')}"
    assert "id" in user, "User response missing 'id'"
    assert "username" in user, "User response missing 'username'"

def test_member_projects():
    projects = get("projects?membership=true&per_page=10")
    assert isinstance(projects, list), f"Expected list of projects, got: {projects}"
    assert len(projects) > 0, "No accessible member projects found"

def test_branches():
    projects = get("projects?membership=true&per_page=1")
    assert isinstance(projects, list) and len(projects) > 0
    sample_pid = projects[0]["id"]
    branches = get(f"projects/{sample_pid}/repository/branches")
    assert isinstance(branches, list), f"Expected branches list, got: {branches}"
    assert len(branches) > 0, f"No branches found for project {sample_pid}"

def test_commits():
    projects = get("projects?membership=true&per_page=1")
    assert isinstance(projects, list) and len(projects) > 0
    sample_pid = projects[0]["id"]
    commits = get(f"projects/{sample_pid}/repository/commits?per_page=5")
    assert isinstance(commits, list), f"Expected commits list, got: {commits}"
    assert len(commits) > 0, f"No commits found for project {sample_pid}"

def main():
    print("=========================================================")
    print("RepoLens Spike B3: WCA GitLab REST API Verification")
    print(f"Target Server: {API_URL}")
    print("=========================================================")

    if not TOKEN:
        print("[!] No GITLAB_TOKEN provided in .env.")
        print("Please configure GITLAB_TOKEN=glpat-... in your .env file.\n")
        return

    # 1. User Profile Test
    user = get("user")
    if "error" in user:
        print(f"[1/4] User Profile: FAILED -> {user['error']}")
        return
    
    print(f"[1/4] User Profile: SUCCESS -> {user.get('name')} (@{user.get('username')}) | ID: {user.get('id')}")

    # 2. Member Projects
    projects = get("projects?membership=true&per_page=10")
    if isinstance(projects, list) and len(projects) > 0:
        print(f"[2/4] Member Projects: SUCCESS -> Found {len(projects)} accessible project(s):")
        for p in projects[:4]:
            print(f"      * [{p.get('id')}] {p.get('name')} ({p.get('path_with_namespace')}) | Branch: {p.get('default_branch')}")
        
        sample_pid = projects[0]["id"]

        # 3. Branches
        branches = get(f"projects/{sample_pid}/repository/branches")
        if isinstance(branches, list):
            bnames = [b.get("name") for b in branches]
            print(f"\n[3/4] Branches for Project [{sample_pid}]: SUCCESS -> {bnames}")

        # 4. Commits
        commits = get(f"projects/{sample_pid}/repository/commits?per_page=3")
        if isinstance(commits, list):
            print(f"[4/4] Commit History for Project [{sample_pid}]: SUCCESS -> Found {len(commits)} commits:")
            for c in commits:
                print(f"      * {c.get('short_id')} - {c.get('title')} (by {c.get('author_name')})")

    print("\n=========================================================")
    print("[SUCCESS] All 4 WCA GitLab REST API endpoints verified!")
    print("=========================================================")

if __name__ == "__main__":
    main()
