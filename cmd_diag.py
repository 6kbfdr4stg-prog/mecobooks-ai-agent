import subprocess
import os

output_path = "/Users/tuankth/.gemini/antigravity/scratch/video_project/cmd_diag.txt"

def run_cmd(cmd):
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return f"CMD: {cmd}\nSTDOUT: {res.stdout}\nSTDERR: {res.stderr}\nCODE: {res.returncode}\n\n"
    except Exception as e:
        return f"CMD: {cmd}\nERROR: {str(e)}\n\n"

with open(output_path, "w") as f:
    f.write(run_cmd("which docker"))
    f.write(run_cmd("docker --version"))
    f.write(run_cmd("docker ps -a"))
    f.write(run_cmd("which cloudflared"))
    f.write(run_cmd("./cloudflared --version"))
    f.write(run_cmd("docker logs video_project_tunnel_1 --tail 50"))
