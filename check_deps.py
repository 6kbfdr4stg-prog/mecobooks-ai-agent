import sys

modules = [
    "fastapi", "uvicorn", "pydantic", "requests", "schedule", 
    "feedparser", "thefuzz", "unidecode", "openai"
]

results = []
for mod in modules:
    try:
        __import__(mod)
        results.append(f"{mod}: OK")
    except ImportError as e:
        results.append(f"{mod}: FAILED ({e})")
    except Exception as e:
        results.append(f"{mod}: ERROR ({e})")

with open("import_test.txt", "w") as f:
    f.write("\n".join(results))
