
import os
import subprocess

def run_kill(cmd):
    try:
        print(f"Running: {cmd}")
        os.system(cmd)
    except Exception as e:
        print(f"Error: {e}")

print("Attempting to force kill Docker processes...")
run_kill("pkill -9 -f Docker")
run_kill("pkill -9 -f 'Docker Desktop'")
run_kill("pkill -9 -f com.docker.backend")
run_kill("pkill -9 -f com.docker.hyperkit")
run_kill("pkill -9 -f com.docker.driver.amd64-linux")
print("Done.")
