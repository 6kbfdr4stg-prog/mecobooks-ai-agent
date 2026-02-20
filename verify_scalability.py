import time
from haravan_client import HaravanClient
from database import get_db_connection

def test_cache():
    client = HaravanClient()
    print("Testing cache effectiveness...")
    
    # 1. First run (should be slow, cache miss)
    start = time.time()
    data1 = client.get_all_products(bypass_cache=False)
    end1 = time.time()
    print(f"Run 1 (Initial): {len(data1)} variants in {end1 - start:.2f}s")
    
    # 2. Second run (should be instant, cache hit)
    start = time.time()
    data2 = client.get_all_products(bypass_cache=False)
    end2 = time.time()
    print(f"Run 2 (Cached): {len(data2)} variants in {end2 - start:.2f}s")
    
    if (end2 - start) < (end1 - start) / 2:
        print("✅ Cache is working perfectly!")
    else:
        print("⚠️ Cache might not be working as expected.")

def test_wal():
    print("Testing WAL mode...")
    conn = get_db_connection()
    c = conn.cursor()
    res = c.execute("PRAGMA journal_mode;").fetchone()
    print(f"Current Journal Mode: {res[0]}")
    if res[0].lower() == "wal":
        print("✅ SQLite WAL mode is ENABLED.")
    else:
        print("❌ SQLite WAL mode is NOT active.")
    conn.close()

if __name__ == "__main__":
    test_wal()
    test_cache()
