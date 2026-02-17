import os
import subprocess

path = "/Users/tuankth/.gemini/antigravity/scratch/video_project/tunnel_found.txt"
try:
    # Try multiple ways to find the container name
    names_output = subprocess.getoutput("docker ps --format '{{.Names}}'")
    with open(path, "w") as f:
        f.write(f"NAMES:\n{names_output}\n\n")
        # Try to find tunnel logs for any container with 'tunnel' in name
        for line in names_output.splitlines():
            if "tunnel" in line:
                f.write(f"LOGS for {line}:\n")
                f.write(subprocess.getoutput(f"docker logs {line} --tail 50"))
                f.write("\n\n")
except Exception as e:
    with open(path, "a") as f:
        f.write(f"ERROR: {str(e)}\n")
