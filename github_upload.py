import requests
import base64
import json

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")  # Token removed for security
REPO = "6kbfdr4stg-prog/mecobooks-ai-agent"
BRANCH = "main"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def get_file_sha(path):
    url = f"https://api.github.com/repos/{REPO}/contents/{path}"
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200:
        return r.json()["sha"]
    return None

def upload_file(local_path, remote_path, commit_msg):
    with open(local_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")
    
    sha = get_file_sha(remote_path)
    
    payload = {
        "message": commit_msg,
        "content": content,
        "branch": BRANCH
    }
    if sha:
        payload["sha"] = sha
    
    url = f"https://api.github.com/repos/{REPO}/contents/{remote_path}"
    r = requests.put(url, headers=HEADERS, json=payload)
    
    if r.status_code in [200, 201]:
        print(f"✅ Uploaded {remote_path}: {r.json().get('commit', {}).get('sha', 'ok')}")
        return True
    else:
        print(f"❌ Failed {remote_path}: {r.status_code} - {r.text[:200]}")
        return False

# Upload files
print("Uploading server.py...")
upload_file("server.py", "server.py", "Add /verify dashboard and /run-agent-sync endpoints")

print("Uploading templates/verification.html...")
upload_file("templates/verification.html", "templates/verification.html", "Add verification dashboard HTML")

print("Uploading ai_agents/inventory_analyst.py...")
upload_file("ai_agents/inventory_analyst.py", "ai_agents/inventory_analyst.py", "Add run() method to InventoryAnalystAgent")

print("Uploading ai_agents/content_creator.py...")
upload_file("ai_agents/content_creator.py", "ai_agents/content_creator.py", "Add run() method to ContentCreatorAgent")

print("Uploading ai_agents/market_research.py...")
upload_file("ai_agents/market_research.py", "ai_agents/market_research.py", "Update MarketResearchAgent run() to return data")

print("Done!")
