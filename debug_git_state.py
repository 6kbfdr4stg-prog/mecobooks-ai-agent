import subprocess

with open("git_debug_log.txt", "w") as f:
    try:
        f.write("--- GIT STATUS ---\n")
        status = subprocess.check_output("git status", shell=True, text=True, stderr=subprocess.STDOUT)
        f.write(status + "\n")
        
        f.write("\n--- GIT LOG ---\n")
        log = subprocess.check_output("git log -n 5 --oneline", shell=True, text=True, stderr=subprocess.STDOUT)
        f.write(log + "\n")
        
        f.write("\n--- REMOTE ---\n")
        remote = subprocess.check_output("git remote -v", shell=True, text=True, stderr=subprocess.STDOUT)
        f.write(remote + "\n")

        # Try push again and capture output
        f.write("\n--- PUSH ATTEMPT ---\n")
        push = subprocess.check_output("git push origin main", shell=True, text=True, stderr=subprocess.STDOUT)
        f.write(push + "\n")
        
    except subprocess.CalledProcessError as e:
        f.write("\nERROR DETAILS:\n")
        f.write(str(e.output))
    except Exception as e:
        f.write("\nEXCEPTION:\n")
        f.write(str(e))
