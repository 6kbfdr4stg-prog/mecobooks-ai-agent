import subprocess

try:
    s = subprocess.check_output("git status", shell=True, text=True)
    print("--- GIT STATUS ---")
    print(s)
    l = subprocess.check_output("git log -n 1", shell=True, text=True)
    print("--- GIT LOG ---")
    print(l)
except Exception as e:
    print(e)
