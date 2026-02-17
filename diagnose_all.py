import os
import subprocess
import socket

def check_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

print("--- DIAGNOSTICS ---")
print(f"Port 5001 open: {check_port(5001)}")
print(f"Port 5000 open: {check_port(5000)}")

print("\n--- DOCKER STATUS ---")
try:
    res = subprocess.run(["docker", "ps", "-a"], capture_output=True, text=True)
    print(res.stdout if res.stdout else "No containers found.")
except Exception as e:
    print(f"Docker command failed: {e}")

print("\n--- PROCESS STATUS ---")
try:
    res = subprocess.run(["ps", "aux"], capture_output=True, text=True)
    lines = [l for l in res.stdout.split('\n') if 'python' in l or 'server' in l or 'main' in l or 'cloudflared' in l]
    print('\n'.join(lines) if lines else "No matching processes found.")
except Exception as e:
    print(f"PS command failed: {e}")

print("\n--- TUNNEL LOGS IF ANY ---")
if os.path.exists("tunnel_final.log"):
     with open("tunnel_final.log", "r") as f:
         print(f.read()[-500:])
