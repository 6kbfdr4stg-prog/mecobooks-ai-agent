import os
import subprocess

def check():
    with open("diag_output.txt", "w") as f:
        f.write("Diagnostic Report\n")
        f.write("=================\n\n")
        
        # Check architecture
        arch = subprocess.getoutput("uname -m")
        f.write(f"Architecture: {arch}\n")
        
        # Check common paths
        paths = ["/opt/homebrew/bin/cloudflared", "/usr/local/bin/cloudflared", "/opt/homebrew/bin/brew", "/usr/local/bin/brew"]
        for p in paths:
            exists = os.path.exists(p)
            f.write(f"{p} exists: {exists}\n")
            
        # Check PATH
        f.write(f"\nPATH: {os.environ.get('PATH', '')}\n")
        
        # Try to find cloudflared
        try:
            cf_path = subprocess.getoutput("which cloudflared")
            f.write(f"\nwhich cloudflared: {cf_path}\n")
        except:
            f.write("\ncloudflared not in which\n")

if __name__ == "__main__":
    check()
