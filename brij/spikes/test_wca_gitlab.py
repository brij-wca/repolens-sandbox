import os
import json
import urllib.request

# Load environment variables from .env if present
env_file = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".env")
if os.path.exists(env_file):
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip() and not line.startswith("#") and "=" in line:
                k, v = line.strip().split("=", 1)
                os.environ.setdefault(k, v)

TOKEN = os.environ.get("GITLAB_TOKEN", "")
BASE_URL = os.environ.get("GITLAB_URL", "http://git.webchiparmor.com:9418").rstrip("/") + "/api/v4"
HEADERS = {"PRIVATE-TOKEN": TOKEN}

def get(endpoint):
    url = f"{BASE_URL}/{endpoint.lstrip('/')}"
    req = urllib.request.Request(url, headers=HEADERS)
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
    print(f"\n[1/4] User Profile: SUCCESS -> {user.get('name')} (@{user.get('username')}) | ID: {user.get('id')}")

def test_member_projects():
    projects = get("projects?membership=true&per_page=10")
    assert isinstance(projects, list), f"Expected list of projects, got: {projects}"
    assert len(projects) > 0, "No accessible member projects found"
    print(f"\n[2/4] Member Projects: SUCCESS -> Found {len(projects)} accessible project(s)")
    for p in projects:
        print(f"      * [{p.get('id')}] {p.get('name')} ({p.get('path_with_namespace')})")

def test_branches():
    projects = get("projects?membership=true&per_page=1")
    assert isinstance(projects, list) and len(projects) > 0
    sample_pid = projects[0]["id"]
    branches = get(f"projects/{sample_pid}/repository/branches")
    assert isinstance(branches, list), f"Expected branches list, got: {branches}"
    assert len(branches) > 0, f"No branches found for project {sample_pid}"
    branch_names = [b.get("name") for b in branches]
    print(f"\n[3/4] Branches for Project [{sample_pid}]: SUCCESS -> {branch_names}")

def test_commits():
    projects = get("projects?membership=true&per_page=1")
    assert isinstance(projects, list) and len(projects) > 0
    sample_pid = projects[0]["id"]
    commits = get(f"projects/{sample_pid}/repository/commits?per_page=5")
    assert isinstance(commits, list), f"Expected commits list, got: {commits}"
    assert len(commits) > 0, f"No commits found for project {sample_pid}"
    print(f"\n[4/4] Commit History for Project [{sample_pid}]: SUCCESS -> Found {len(commits)} commits")
    for c in commits[:3]:
        print(f"      * {c.get('short_id')} - {c.get('title')} (by {c.get('author_name')})")

def main():
    print("=========================================================")
    print("Live WCA GitLab API Endpoint Validation (Task B3)")
    print(f"Target Server: {BASE_URL}")
    print("=========================================================")
    try:
        test_user_profile()
        test_member_projects()
        test_branches()
        test_commits()
        print("\n=========================================================")
        print("[SUCCESS] All 4 WCA GitLab REST API endpoints verified!")
        print("=========================================================")
    except AssertionError as e:
        print(f"\n[FAILED] Test assertion failed: {e}")

if __name__ == "__main__":
    main()
