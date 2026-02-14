from woocommerce import API
import os
import json

class WooCommerceClient:
    def __init__(self):
        self.url = os.environ.get("WOO_URL", "https://mecobooks.com")
        self.key = os.environ.get("WOO_CONSUMER_KEY")
        self.secret = os.environ.get("WOO_CONSUMER_SECRET")
        
        if self.key and self.secret:
            self.wcapi = API(
                url=self.url,
                consumer_key=self.key,
                consumer_secret=self.secret,
                version="wc/v3",
                timeout=10
            )
        else:
            self.wcapi = None
            print("WooCommerce API Credentials missing")

    def search_products(self, query, limit=5):
        """
        Search products in WooCommerce by name.
        """
        if not self.wcapi:
            return []

        try:
            # Search for products
            products = self.wcapi.get("products", params={"search": query, "per_page": limit}).json()
            
            results = []
            for p in products:
                # Extract image
                image_url = ""
                if p.get("images") and len(p["images"]) > 0:
                    image_url = p["images"][0]["src"]
                
                # Clean description (remove HTML tags if needed, or keep for web)
                # For simplicity, we just take the name and price for now
                
                results.append({
                    "title": p["name"],
                    "price": f"{int(float(p['price'] or 0)):,}", # Format 100000 -> 100,000
                    "image": image_url,
                    "url": p["permalink"],
                    "description": p.get("short_description", "")
                })
            return results
        except Exception as e:
            print(f"WooCommerce Search Error: {e}")
            return []
