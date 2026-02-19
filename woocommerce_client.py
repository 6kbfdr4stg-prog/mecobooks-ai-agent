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

    def get_tag_id_by_name(self, tag_name):
        """
        Find a WooCommerce Tag ID by its name (case-insensitive).
        """
        if not self.wcapi: return None
        try:
            params = {"search": tag_name, "per_page": 10}
            tags = self.wcapi.get("products/tags", params=params).json()
            if isinstance(tags, list):
                from unidecode import unidecode
                tag_name_norm = unidecode(tag_name).lower()
                for t in tags:
                    if unidecode(t['name']).lower() == tag_name_norm:
                        return t['id']
            return None
        except Exception as e:
            print(f"Tag Search Error: {e}")
            return None

    def search_products(self, query, limit=5, author=None):
        """
        Search products in WooCommerce by name.
        """
        if not self.wcapi or not query:
            return []

        from unidecode import unidecode
        from thefuzz import fuzz
        
        results_dict = {} # Use dict to deduplicate by ID key
        
        # 1. Try Direct Slug Match first (Fastest & Most Accurate)
        slug = unidecode(query).lower().replace(" ", "-")
        try:
            slug_products = self.wcapi.get("products", params={"slug": slug}).json()
            if isinstance(slug_products, list):
                for p in slug_products:
                    results_dict[p['id']] = p
        except Exception as e:
            print(f"Slug Search Error: {e}")

        # 2. Loose Keyword Search (High Recall)
        params = {
            "search": query, 
            "per_page": 50, # Increase limit
            "status": "publish"
        }
        
        try:
            loose_products = self.wcapi.get("products", params=params).json()
            if isinstance(loose_products, list):
                for p in loose_products:
                    if p['id'] not in results_dict:
                        results_dict[p['id']] = p
        except Exception as e:
             print(f"Loose Search Error: {e}")
        
        # 3. TAG SEARCH (New Fallback for Authors)
        # If query or author matches a tag, pull products for that tag
        tag_search_term = author if author else query
        tag_id = self.get_tag_id_by_name(tag_search_term)
        if tag_id:
            try:
                print(f"🏷️ Found Tag ID {tag_id} for '{tag_search_term}'. Fetching tagged products...")
                tag_products = self.wcapi.get("products", params={"tag": tag_id, "per_page": 20, "status": "publish"}).json()
                if isinstance(tag_products, list):
                    for p in tag_products:
                        if p['id'] not in results_dict:
                            # Boost products from tag search
                            p['_tag_boost'] = True 
                            results_dict[p['id']] = p
            except Exception as e:
                print(f"Tag Products Fetch Error: {e}")

        # Convert back to list
        products = list(results_dict.values())
        
        results = []
        for p in products:
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
        query_norm = unidecode(query).lower()
        
        for index, p in enumerate(results):
            title_norm = unidecode(p['title']).lower()
            
            # Calculate scores
            score = fuzz.token_set_ratio(query_norm, title_norm)
            
            # Boost if exact substring match in title (after normalization)
            if query_norm in title_norm:
                score += 20 
                
            # Tag Boost
            if p.get('_tag_boost'):
                score += 40 # Significant boost for tag matches
                
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
                     "per_page": 100, 
                     "orderby": "popularity",
                     "status": "publish"
                }
                pop_products = self.wcapi.get("products", params=pop_params).json()
                
                if isinstance(pop_products, list):
                    self._process_fallback_products(pop_products, query_norm, results, results_dict)
            except Exception as e:
                print(f"Propularity Search Error: {e}")

            # 3. Newest Search (Client-side Filter - incase new item)
            try:
                new_params = {
                     "per_page": 100,
                     "orderby": "date",
                     "order": "desc",
                     "status": "publish"
                }
                new_products = self.wcapi.get("products", params=new_params).json()
                
                if isinstance(new_products, list):
                   self._process_fallback_products(new_products, query_norm, results, results_dict)
            except: pass
            
            # 4. SPECIFIC KEYWORD FIX (For broken search index on server)
            # Normalize check:
            check_key = query_norm.replace("-", " ")
            
            # FIX 1: Đắc Nhân Tâm -> Dale Carnegie
            if "dac nhan tam" in check_key:
                 try:
                    auth_params = {"search": "Dale Carnegie", "per_page": 20, "status": "publish"}
                    auth_products = self.wcapi.get("products", params=auth_params).json()
                    if isinstance(auth_products, list):
                        self._process_fallback_products(auth_products, query_norm, results, results_dict)
                 except: pass

            # FIX 2: Dạy con làm giàu -> Robert Kiyosaki
            if "day con lam giau" in check_key or "rich dad" in check_key:
                 try:
                    auth_params = {"search": "Kiyosaki", "per_page": 20, "status": "publish"}
                    auth_products = self.wcapi.get("products", params=auth_params).json()
                    if isinstance(auth_products, list):
                        self._process_fallback_products(auth_products, query_norm, results, results_dict)
                 except: pass

            # 5. AI-INFERRED AUTHOR FALLBACK (The General Mechanism)
            if author and best_score < 70:
                 try:
                    print(f"Triggering Author Fallback: '{author}'")
                    auth_params = {"search": author, "per_page": 20, "status": "publish"}
                    auth_products = self.wcapi.get("products", params=auth_params).json()
                    if isinstance(auth_products, list):
                        self._process_fallback_products(auth_products, query_norm, results, results_dict)
                 except: pass

            # Re-sort after fallbacks
            def stock_priority(item):
                status = item.get('stock_status', 'outofstock')
                if status == 'instock': return 0
                if status == 'onbackorder': return 1
                return 2

            results.sort(key=lambda x: (stock_priority(x), -x['_score']))
            
        return results[:limit]
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
    def get_sales_report(self, period="month"):
        """
        Fetch sales reports from WooCommerce.
        period: 'week', 'month', 'last_month', 'year'.
        """
        if not self.wcapi: return {}
        
        try:
            params = {"period": period}
            reports = self.wcapi.get("reports/sales", params=params).json()
            if isinstance(reports, list) and len(reports) > 0:
                return reports[0] # Return the first report object
            return {}
        except Exception as e:
            print(f"WooCommerce Sales Report Error: {e}")
            return {}

    def get_system_status(self):
        """
        Fetch system status (for inventory counts).
        """
        if not self.wcapi: return {}
        try:
            # We can't get full status easily via API v3 without permissions, 
            # so we'll do a quick product count via /products header or count endpoint
            # Actually, reports/products/count is good
            count = self.wcapi.get("reports/products/count").json()
            return count if isinstance(count, list) else []
        except Exception as e:
            print(f"WooCommerce Status Error: {e}")
            return []
