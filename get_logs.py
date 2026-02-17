import subprocess
import os

path = "/Users/tuankth/.gemini/antigravity/scratch/video_project/tunnel_logs_final.txt"
try:
    with open(path, "w") as f:
        f.write("DOCKER PS:\n")
        f.write(subprocess.getoutput("docker ps -a"))
        f.write("\n\nTUNNEL LOGS:\n")
        f.write(subprocess.getoutput("docker-compose logs tunnel"))
        f.write("\n\nEND\n")
except Exception as e:
    with open(path + ".err", "w") as f:
        f.write(str(e))
