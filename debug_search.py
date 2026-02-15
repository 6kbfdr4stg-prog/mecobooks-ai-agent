from woocommerce_client import WooCommerceClient

def test_search():
    client = WooCommerceClient()
    # Credentials should be loaded from env vars or config.py in real usage
    # Ensure WOO_URL, WOO_CONSUMER_KEY, WOO_CONSUMER_SECRET are set in environment
    
    query = "nghĩ giàu"  # Use a query likely to return results
    products = client.search_products(query)
    
    if not products:
        print("No products found.")
        return

    print(f"Found {len(products)} products:")
    for p in products:
        print(f"- {p['title']} ({p['price']})")
        print(f"  Stock Status: {p.get('stock_status')}")
        print(f"  Inventory Text: {p.get('inventory_text')}")
        print(f"  URL: {p['url']}")
        print("---")

if __name__ == "__main__":
    test_search()
