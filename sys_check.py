import subprocess
import os

def check():
    results = []
    
    # Check processes
    ps = subprocess.run(["ps", "aux"], capture_output=True, text=True)
    results.append("--- PS AUX ---")
    results.append(ps.stdout)
    
    # Check netstat/lsof (Mac uses lsof)
    ls = subprocess.run(["lsof", "-i", ":5001"], capture_output=True, text=True)
    results.append("--- LSOF :5001 ---")
    results.append(ls.stdout)
    
    ls8 = subprocess.run(["lsof", "-i", ":8000"], capture_output=True, text=True)
    results.append("--- LSOF :8000 ---")
    results.append(ls8.stdout)

    with open("system_check.txt", "w") as f:
        f.write("\n".join(results))

if __name__ == "__main__":
    check()
