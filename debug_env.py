
import os
from dotenv import load_dotenv

print(f"Current working directory: {os.getcwd()}")
print(f".env exists: {os.path.exists('.env')}")

load_dotenv()

key = os.environ.get("GEMINI_API_KEY")
print(f"GEMINI_API_KEY loaded: {'Yes' if key else 'No'}")
if key:
    print(f"Key length: {len(key)}")
