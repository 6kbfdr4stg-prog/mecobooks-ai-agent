import subprocess
import os

path = "/Users/tuankth/.gemini/antigravity/scratch/video_project/git_diag.txt"

def run_cmd(cmd):
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return f"CMD: {cmd}\nSTDOUT: {res.stdout}\nSTDERR: {res.stderr}\n"
    except Exception as e:
        return f"CMD: {cmd}\nERROR: {str(e)}\n"

with open(path, "w") as f:
    f.write(run_cmd("git remote -v"))
    f.write(run_cmd("git status"))
    f.write(run_cmd("git branch"))
