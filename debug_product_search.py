
from woocommerce_client import WooCommerceClient

def test_search():
    woo = WooCommerceClient()
    query = "dạy con làm giàu"
    
    print(f"🔎 Testing Search for: '{query}'")
    print("\n--- Running woo.search_products (Final Verification) ---")
    results = woo.search_products(query, limit=10)
    
    if results:
        print(f"✅ Found {len(results)} products:")
        for i, p in enumerate(results):
            print(f"{i+1}. [{p['id']}] {p['title']}")
            print(f"   Status: {p.get('stock_status')} (Text: {p.get('inventory_text')})")
            print(f"   Image: {p.get('image')}")
    else:
        print("❌ No products found.")

if __name__ == "__main__":
    test_search()
