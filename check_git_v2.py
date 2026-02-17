import subprocess

with open("git_status_final.txt", "w") as f:
    try:
        s = subprocess.check_output("git status", shell=True, text=True)
        f.write("--- GIT STATUS ---\n")
        f.write(s)
        l = subprocess.check_output("git log -n 1", shell=True, text=True)
        f.write("\n--- GIT LOG ---\n")
        f.write(l)
    except Exception as e:
        f.write(str(e))
