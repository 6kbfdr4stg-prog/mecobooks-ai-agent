import urllib.request
import os
import sys

url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-arm64"
dest = "/Users/tuankth/.gemini/antigravity/scratch/video_project/cloudflared_bin"

print(f"URL: {url}")
print(f"Dest: {dest}")

try:
    print("Starting download...")
    response = urllib.request.urlopen(url)
    data = response.read()
    print(f"Data length: {len(data)}")
    
    with open(dest, "wb") as f:
        f.write(data)
    
    os.chmod(dest, 0o755)
    print("Download finished and permissions set.")
    
    if len(data) > 1000000:
        print("Success: File seems to be a real binary.")
except Exception as e:
    print(f"FAILURE: {e}")
    sys.exit(1)
