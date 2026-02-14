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
            results_dict = {} # Use dict to deduplicate by ID key
            from unidecode import unidecode
            
            # 1. Try Exact Slug Match (High Precision)
            # Useful for "Nhà giả kim" -> "nha-gia-kim"
            slug = unidecode(query).lower().replace(" ", "-")
            try:
                slug_products = self.wcapi.get("products", params={"slug": slug}).json()
                if isinstance(slug_products, list):
                    for p in slug_products:
                        results_dict[p['id']] = p
            except Exception as e:
                print(f"Slug Search Error: {e}")

            # 2. Loose Keyword Search (High Recall)
            # Fetch more (50) to handle loose API search matching
            loose_products = self.wcapi.get("products", params={"search": query, "per_page": 50}).json()
            if isinstance(loose_products, list):
                for p in loose_products:
                    if p['id'] not in results_dict:
                        results_dict[p['id']] = p
            
            # Convert back to list
            products = list(results_dict.values())
            
            results = []
            for p in products:
                # Extract image
                # Extract image
                image_url = "https://placehold.co/300x300?text=No+Image" # Default fallback
                
                # Check standard images
                if p.get("images") and len(p["images"]) > 0:
                    image_url = p["images"][0]["src"]
                
                # Check Woo External Images (meta_data)
                elif p.get("meta_data"):
                    for meta in p["meta_data"]:
                        if meta.get("key") == "_ext_featured_url" and meta.get("value"):
                            image_url = meta["value"]
                            break
                            
                # Clean description (remove HTML tags if needed, or keep for web)
                # For simplicity, we just take the name and price for now
                
                # Extract stock info
                stock_status = p.get("stock_status", "instock") 
                stock_quantity = p.get("stock_quantity")
                
                inventory_text = "Còn hàng"
                if stock_status == "outofstock":
                    inventory_text = "Hết hàng"
                elif stock_status == "onbackorder":
                    inventory_text = "Đặt trước"
                elif stock_quantity is not None:
                     inventory_text = f"Còn {stock_quantity}"

                results.append({
                    "title": p["name"],
                    "price": f"{int(float(p['price'] or 0)):,}", # Format 100000 -> 100,000
                    "image": image_url,
                    "url": p["permalink"],
                    "description": p.get("short_description", ""),
                    "stock_status": stock_status,
                    "inventory_text": inventory_text
                })
            
            
            # Fuzzy Sort Logic
            from thefuzz import fuzz
            from unidecode import unidecode
            
            # Normalize query: remove accents, lowercase
            query_norm = unidecode(query).lower()
            
            for index, p in enumerate(results):
                title_norm = unidecode(p['title']).lower()
                
                # Calculate scores
                # 1. Token Set Ratio: Matches overlapping words efficiently (e.g. "sach giao khoa" matches "Giao trinh Sach Giao Khoa")
                # 2. Partial Ratio: Matches substring
                score = fuzz.token_set_ratio(query_norm, title_norm)
                
                # Boost if exact substring match in title (after normalization)
                if query_norm in title_norm:
                    score += 20 
                    
                # Cap at 100? No, let strict matches go higher (120) for sorting
                p['_score'] = score
            
            # Sort by score descending
            results.sort(key=lambda x: x['_score'], reverse=True)
            
            # Filter low relevance if needed (e.g. < 50)
            # results = [r for r in results if r['_score'] >= 50]
            
            return results[:limit]
        except Exception as e:
            print(f"WooCommerce Search Error: {e}")
            return []
