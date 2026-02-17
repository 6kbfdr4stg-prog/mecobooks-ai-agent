import subprocess
import os
import sys

output_file = "/Users/tuankth/.gemini/antigravity/scratch/video_project/env_diag.txt"

with open(output_file, "w") as f:
    f.write(f"CWD: {os.getcwd()}\n")
    f.write(f"PATH: {os.environ.get('PATH')}\n")
    f.write(f"Python: {sys.executable}\n")
    
    for cmd in ["docker", "docker-compose", "cloudflared"]:
        try:
            path = subprocess.getoutput(f"which {cmd}")
            f.write(f"{cmd} path: {path}\n")
            if path:
                version = subprocess.getoutput(f"{cmd} --version")
                f.write(f"{cmd} version: {version}\n")
        except Exception as e:
            f.write(f"Error checking {cmd}: {str(e)}\n")
    
    try:
        f.write("\n--- DOCKER PS ---\n")
        f.write(subprocess.getoutput("docker ps -a"))
    except Exception as e:
        f.write(f"Docker ps failed: {str(e)}\n")

    f.write("\n--- END ---\n")
