import requests
from config import HARAVAN_SHOP_URL, HARAVAN_ACCESS_TOKEN
from datetime import datetime, timedelta

def debug_haravan_orders():
    headers = {
        "Authorization": f"Bearer {HARAVAN_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # test 1: Fetch without filter to see what exists
    endpoint = f"{HARAVAN_SHOP_URL.rstrip('/')}/admin/orders.json"
    params = {
        "limit": 5,
        "status": "any",
        "fields": "id,name,total_price,created_at"
    }
    
    print("--- Test 1: Last 5 orders without date filter ---")
    try:
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()
        orders = response.json().get('orders', [])
        print(f"Fetched {len(orders)} orders.")
        for o in orders:
            print(f"Order: {o.get('name')}, Price: {o.get('total_price')}, Created: {o.get('created_at')}")
    except Exception as e:
        print(f"Error Test 1: {e}")

    # test 2: Test current month filter
    now = datetime.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    # Most APIs prefer YYYY-MM-DDTHH:MM:SS format
    iso_date = start_of_month.strftime("%Y-%m-%dT%H:%M:%S")
    
    print(f"\n--- Test 2: Filter from {iso_date} ---")
    params["created_at_min"] = iso_date
    try:
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()
        orders = response.json().get('orders', [])
        print(f"Fetched {len(orders)} orders with filter.")
    except Exception as e:
        print(f"Error Test 2: {e}")

if __name__ == "__main__":
    debug_haravan_orders()
