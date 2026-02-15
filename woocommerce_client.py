from woocommerce import API
import os
import json
from dotenv import load_dotenv

load_dotenv()

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
            # Improve API search: Sort by 'relevance' (default) but requests often fail to rank well.
            # Let's try fetching more and filtering client side, or use 'include' if we had tag inputs.
            # Strategy:
            # - Search with `orderby=relevance` (default)
            # - ALSO Search with `orderby=popularity` (sales) to capture top sellers matching the keyword? 
            #   No, API doesn't allow OR.
            
            # Let's just fetch a larger batch (100) to ensure we capture the item if it's buried.
            # And maybe use a stricter search param if possible? No, 'search' is the only one.
            
            params = {
                "search": query, 
                "per_page": 50, # Increase limit
                "status": "publish"
            }
            
            loose_products = self.wcapi.get("products", params=params).json()
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
                
                # Safely extract price
                try:
                    price_val = int(float(p.get('price') or 0))
                    price_fmt = f"{price_val:,}"
                except (ValueError, TypeError):
                    price_fmt = "0"

                # Extract stock info safely
                stock_status = p.get("stock_status", "instock") 
                stock_quantity = p.get("stock_quantity")
                
                inventory_text = "Còn hàng"
                if stock_status == "outofstock":
                    inventory_text = "Hết hàng"
                elif stock_status == "onbackorder":
                    inventory_text = "Đặt trước"
                elif stock_quantity is not None:
                     inventory_text = f"Còn {stock_quantity}"

                # Extract sales data
                total_sales = p.get("total_sales", 0)

                results.append({
                    "title": p.get("name", "Sản phẩm không tên"),
                    "price": price_fmt,
                    "image": image_url,
                    "url": p.get("permalink", "#"),
                    "description": p.get("short_description", ""),
                    "stock_status": stock_status,
                    "inventory_text": inventory_text,
                    "total_sales": total_sales,
                    "id": p['id']
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
            
            # CHECK QUALITY
            best_score = results[0]['_score'] if results else 0
            
            # FALLBACK STRATEGY: IF POOR MATCH (<60), TRY AGGRESSIVE SEARCH
            if best_score < 60:
                print(f"Low relevance ({best_score}). Trying Aggressive Fallback...")
                
                # 1. Unaccented Search
                try:
                    query_un = unidecode(query)
                    if query_un != query:
                        un_params = {"search": query_un, "per_page": 20, "status": "publish"}
                        un_products = self.wcapi.get("products", params=un_params).json()
                        if isinstance(un_products, list):
                            self._process_fallback_products(un_products, query_norm, results, results_dict)
                except: pass

                # 2. Popularity Search (Client-side Filter)
                try:
                    pop_params = {
                         "per_page": 100, # Increased from 50 to 100
                         "orderby": "popularity",
                         "status": "publish"
                    }
                    pop_products = self.wcapi.get("products", params=pop_params).json()
                    
                    if isinstance(pop_products, list):
                        self._process_fallback_products(pop_products, query_norm, results, results_dict)
                except Exception as e:
                    print(f"Fallback Popularity Error: {e}")
                    
                # 3. Newest Search (Client-side Filter - incase new item)
                try:
                    new_params = {
                         "per_page": 100, # Increased from 50 to 100
                         "orderby": "date",
                         "status": "publish"
                    }
                    new_products = self.wcapi.get("products", params=new_params).json()
                    if isinstance(new_products, list):
                        self._process_fallback_products(new_products, query_norm, results, results_dict)
                except: pass
            
            # 4. SPECIFIC KEYWORD FIX (For broken search index on server)
            # "Đắc Nhân Tâm" fails on search, but "Dale Carnegie" works.
            # Normalize check:
            check_key = query_norm.replace("-", " ")
            if "dac nhan tam" in check_key:
                 try:
                    auth_params = {"search": "Dale Carnegie", "per_page": 20, "status": "publish"}
                    auth_products = self.wcapi.get("products", params=auth_params).json()
                    if isinstance(auth_products, list):
                        self._process_fallback_products(auth_products, query_norm, results, results_dict)
                 except: pass

            # Re-sort after fallback: 
            # 1. Stock Status (instock > others)
            # 2. Score (descending)
            def stock_priority(item):
                status = item.get('stock_status', 'outofstock')
                if status == 'instock': return 0
                if status == 'onbackorder': return 1
                return 2

            results.sort(key=lambda x: (stock_priority(x), -x['_score']))
            
            return results[:limit]
        except Exception as e:
            print(f"WooCommerce Search Error: {e}")
            return []

    def _process_fallback_products(self, product_list, query_norm, results, results_dict):
        """Helper to process and score fallback products"""
        from unidecode import unidecode
        from thefuzz import fuzz
        
        for p in product_list:
            # Calculate score against query
            title_norm_p = unidecode(p['name']).lower()
            
            # Basic fuzzy
            score_p = fuzz.token_set_ratio(query_norm, title_norm_p)
            
            # Boosts
            if query_norm in title_norm_p:
                score_p += 30 # Strong boost for substring match
            
            # If "dac nhan tam" matches "dac nhan tam - dale carnegie" -> 100 partial?
            # Partial ratio is good here
            partial_score = fuzz.partial_ratio(query_norm, title_norm_p)
            if partial_score > 90:
                score_p = max(score_p, 85)
                
            if score_p > 50: # Only add decent matches
                id_ = p['id']
                if id_ not in results_dict:
                    # Process and add
                    inventory_text = "Còn hàng" 
                    if p.get("stock_status") == "outofstock": inventory_text = "Hết hàng"
                    elif p.get("stock_status") == "onbackorder": inventory_text = "Đặt trước"
                    
                    # Extract image
                    image_url = "https://placehold.co/300x300?text=No+Image"
                    if p.get("images") and len(p["images"]) > 0:
                        image_url = p["images"][0]["src"]
                    elif p.get("meta_data"):
                         for meta in p["meta_data"]:
                            if meta.get("key") == "_ext_featured_url" and meta.get("value"):
                                image_url = meta["value"]
                                break
                    
                    new_item = {
                        "title": p.get("name", ""),
                        "price": f"{int(float(p.get('price') or 0)):,}",
                        "image": image_url,
                        "url": p.get("permalink", "#"),
                        "stock_status": p.get("stock_status"),
                        "inventory_text": inventory_text,
                        "id": p['id'],
                        "_score": score_p
                    }
                    results.append(new_item)
                    results_dict[id_] = new_item

    def get_orders(self, after=None, before=None, status="completed", limit=20):
        """
        Fetch orders for email marketing.
        after/before: ISO 8601 string (e.g., '2023-10-25T00:00:00')
        """
        if not self.wcapi: return []
        
        params = {"status": status, "per_page": limit}
        if after: params["after"] = after
        if before: params["before"] = before
        
        try:
            return self.wcapi.get("orders", params=params).json()
        except Exception as e:
            print(f"WooCommerce Order Fetch Error: {e}")
            return []

    def create_order(self, data):
        """
        Create a new order in WooCommerce.
        data: dict containing 'line_items', 'billing', 'shipping'
        """
        if not self.wcapi: return None
        
        try:
            response = self.wcapi.post("orders", data).json()
            if 'id' in response:
                return response
            else:
                print(f"WooCommerce Order Creation Failed: {response}")
                return None
        except Exception as e:
            print(f"WooCommerce Order Creation Error: {e}")
            return None

    def get_products(self, limit=10, orderby="date", order="desc", category=None):
        """
        Fetch products with sorting/filtering (for Best Sellers/Upsell).
        """
        if not self.wcapi: return []
        
        params = {
            "per_page": limit,
            "orderby": orderby,
            "order": order,
            "status": "publish"
        }
        if category:
            params["category"] = category
            
        try:
            return self.wcapi.get("products", params=params).json()
        except Exception as e:
            print(f"WooCommerce Get Products Error: {e}")
            return []

    def get_order_by_id(self, order_id):
        """
        Fetch a specific order by ID.
        """
        if not self.wcapi: return None
        
        try:
            # Remove # if present
            clean_id = str(order_id).replace("#", "").strip()
            response = self.wcapi.get(f"orders/{clean_id}").json()
            if 'id' in response:
                return response
            return None
        except Exception as e:
            print(f"WooCommerce Get Order Error: {e}")
            return None
