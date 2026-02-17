import subprocess
import time
import os

cwd = "/Users/tuankth/.gemini/antigravity/scratch/video_project"
os.chdir(cwd)

print(f"Starting server in {cwd}...")
server_proc = subprocess.Popen(["python3", "server.py"], stdout=open("server_diag.log", "w"), stderr=subprocess.STDOUT)
time.sleep(2)

print("Starting tunnel...")
tunnel_proc = subprocess.Popen(["./cloudflared", "tunnel", "--url", "http://localhost:5001"], stdout=open("tunnel_diag.log", "w"), stderr=subprocess.STDOUT)

time.sleep(15)

print("Done waiting.")
