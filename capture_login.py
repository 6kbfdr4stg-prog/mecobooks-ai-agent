import subprocess
import os
import time

# Use the cloudflared binary in the project directory
cloudflared_path = "/Users/tuankth/.gemini/antigravity/scratch/video_project/cloudflared"
output_file = "/Users/tuankth/.gemini/antigravity/scratch/video_project/login_url.txt"

# Run the login command. 
# Note: cloudflared login prints the URL and waits.
# We want to capture the URL and then we can let the process stay or kill it.
# Actually, it prints to stdout and stderr.

try:
    # Start the process
    process = subprocess.Popen(
        [cloudflared_path, "tunnel", "login"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # We only need the first few lines to get the URL
    url = ""
    start_time = time.time()
    while time.time() - start_time < 10: # wait up to 10 seconds
        line = process.stderr.readline()
        if not line:
            line = process.stdout.readline()
        
        if "https://" in line and "dash.cloudflare.com" in line:
            url = line.strip()
            break
        
        if not line and process.poll() is not None:
            break

    with open(output_file, "w") as f:
        if url:
            f.write(url)
        else:
            f.write("URL not found in 10 seconds. Check logs.\n")
            
except Exception as e:
    with open(output_file, "w") as f:
        f.write(f"Error: {str(e)}")
