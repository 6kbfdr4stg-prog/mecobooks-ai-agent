import urllib.request
import os

url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-arm64"
dest = "/Users/tuankth/.gemini/antigravity/scratch/video_project/cloudflared"

print(f"Downloading {url} to {dest}...")
try:
    urllib.request.urlretrieve(url, dest)
    os.chmod(dest, 0o755)
    print("Download successful and permissions set.")
    size = os.path.getsize(dest)
    print(f"File size: {size} bytes")
except Exception as e:
    print(f"Error: {e}")
