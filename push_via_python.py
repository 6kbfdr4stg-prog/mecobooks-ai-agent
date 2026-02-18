import subprocess
import os
import datetime

log_file = "python_push_log.txt"

def run_cmd(cmd):
    with open(log_file, "a") as f:
        f.write(f"\n--- {datetime.datetime.now()} ---\nRunning: {cmd}\n")
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            f.write(f"STDOUT:\n{result.stdout}\n")
            f.write(f"STDERR:\n{result.stderr}\n")
            f.write(f"Return Code: {result.returncode}\n")
            return result.returncode
        except Exception as e:
            f.write(f"EXCEPTION: {e}\n")
            return -1

# Reset log
with open(log_file, "w") as f:
    f.write("Starting Python Push...\n")

# Commands
# Token removed for security - use git credential manager
run_cmd("git add .")
run_cmd('git commit -m "Python Push Verify Dashboard"')
run_cmd("git push origin main")
