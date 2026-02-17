import os
import subprocess

print("Stopping local chat processes...")
try:
    # Kill process on 5001
    subprocess.run(["pkill", "-f", "server.py"], check=False)
    subprocess.run(["pkill", "-f", "main.py"], check=False)
    print("Kill commands sent.")
except Exception as e:
    print(f"Error killing processes: {e}")
