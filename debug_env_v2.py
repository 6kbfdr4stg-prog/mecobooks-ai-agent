import os
import sys
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, ".env")

print(f"Checking for .env at: {env_path}")
print(f"File exists: {os.path.exists(env_path)}")

try:
    with open(env_path, 'r') as f:
        content = f.read()
        print(f"File readable. Content length: {len(content)}")
        if 'TELEGRAM_BOT_TOKEN' in content:
            print("TELEGRAM_BOT_TOKEN found in file.")
        else:
            print("TELEGRAM_BOT_TOKEN NOT found in file.")
except Exception as e:
    print(f"Error reading file: {e}")

success = load_dotenv(env_path, override=True)
print(f"load_dotenv result: {success}")
print(f"TOKEN in os.environ: {os.environ.get('TELEGRAM_BOT_TOKEN') is not None}")
