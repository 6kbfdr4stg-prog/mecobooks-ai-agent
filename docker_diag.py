import os
import subprocess

def run(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
    except Exception as e:
        return str(e)

with open("docker_diag.txt", "w") as f:
    f.write("--- DOCKER PS ---\n")
    f.write(run("docker ps -a"))
    f.write("\n--- TUNNEL LOGS ---\n")
    f.write(run("docker logs video_project_tunnel_1 --tail 100"))
    f.write("\n--- PING LOCALHOST:5001 ---\n")
    f.write(run("curl -s http://localhost:5001/health || echo 'curl failed'"))
