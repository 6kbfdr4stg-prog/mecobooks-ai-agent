import subprocess

def run_git(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(f"CMD: {cmd}")
    print(f"STDOUT:\n{result.stdout}")
    print(f"STDERR:\n{result.stderr}")

run_git("git status")
