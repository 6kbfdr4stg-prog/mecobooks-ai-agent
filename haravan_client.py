import requests
import json
import os
from config import HARAVAN_SHOP_URL, HARAVAN_ACCESS_TOKEN, get_now_hanoi
from utils.cache_manager import cache
from utils.event_manager import event_manager

class HaravanClient:
    def __init__(self, shop_url=HARAVAN_SHOP_URL, access_token=HARAVAN_ACCESS_TOKEN):
        self.shop_url = shop_url.rstrip('/')
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def get_products(self, limit=10, page=1):
        """Fetch a list of products from Haravan (single page)."""
        endpoint = f"{self.shop_url}/admin/products.json"
        params = {
            "limit": limit,
            "page": page,
            "fields": "id,title,body_html,images,variants,sku,handle"
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            products = response.json().get('products', [])
            
            # Expand products into individual variants for sync purposes
            flat_variants = []
            for p in products:
                flat_variants.extend(self.extract_product_variants(p))
            return flat_variants
        except requests.exceptions.RequestException as e:
            print(f"Error fetching products: {e}")
            return []

    def get_all_products(self, bypass_cache=False):
        """Fetch ALL products from Haravan using pagination (with 1-hour cache)."""
        cache_key = "haravan_all_products_v2"
        if not bypass_cache:
            cached_data = cache.get(cache_key)
            if cached_data:
                print(f"✨ [Cache] Loaded {len(cached_data)} variants from cache.")
                return cached_data

        all_variants = []
        page = 1
        limit = 250 # Max per page
        
        print(f"🚀 Starting full catalog fetch from Haravan...")
        while True:
            print(f"📥 Fetching page {page}...")
            variants = self.get_products(limit=limit, page=page)
            if not variants:
                break
            
            all_variants.extend(variants)
            msg = f"✅ Page {page} fetched. Total variants so far: {len(all_variants)}"
            print(msg)
            event_manager.emit("api_progress", msg, {"source": "haravan", "page": page, "total": len(all_variants)})
            
            # Since get_products expands to variants, we check if we got some items
            # If we got less than 250 products (approx), it might be the last page.
            # But get_products returns variants. Let's just rely on NO variants returned.
            
            page += 1
            if page > 200: break # Safety break
            
        # Store in cache for 1 hour
        if all_variants:
            cache.set(cache_key, all_variants, timeout=3600)
            
        return all_variants

    def extract_product_data(self, product):
        """Deprecated: Use extract_product_variants instead for multi-variant support."""
        variants = self.extract_product_variants(product)
        return variants[0] if variants else {}

    def extract_product_variants(self, product):
        """Extract all variants as separate syncable items."""
        items = []
        product_id = product.get('id')
        product_title = product.get('title')
        description = product.get('body_html', '')
        images = [img['src'] for img in product.get('images', [])][:10]
        handle = product.get('handle')
        
        for variant in product.get('variants', []):
            variant_id = variant.get('id')
            sku = variant.get('sku')
            
            # Fallback SKU logic from GAS reference
            if not sku:
                sku = f"HRV-{product_id}-{variant_id}"
                
            items.append({
                "id": product_id,
                "variant_id": variant_id,
                "title": f"{product_title} - {variant.get('title')}" if variant.get('title') != "Default Title" else product_title,
                "product_name": product_title,
                "description": description,
                "price": variant.get('price', 0),
                "sku": sku,
                "inventory_quantity": variant.get('inventory_quantity', 0),
                "handle": handle,
                "images": images
            })
        return items

    def search_products(self, query, limit=5):
        """Search products by title."""
        endpoint = f"{self.shop_url}/admin/products.json"
        params = {
            "title": query,
            "limit": limit,
            "fields": "id,title,body_html,images,variants,handle"
        }
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            products = response.json().get('products', [])
            return [self.extract_product_data(p) for p in products]
        except requests.exceptions.RequestException as e:
            print(f"Error searching products: {e}")
            return []

    def get_product_by_id(self, product_id):
        """Get a single product by ID."""
        endpoint = f"{self.shop_url}/admin/products/{product_id}.json"
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            product = response.json().get('product')
            if product:
                return self.extract_product_data(product)
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error getting product {product_id}: {e}")
            return None

    def get_orders(self, limit=5, status='any', after=None, before=None):
        """Fetch latest orders with optional date filters."""
        endpoint = f"{self.shop_url}/admin/orders.json"
        params = {
            "limit": limit,
            "status": status,
            "fields": "id,name,email,financial_status,fulfillment_status,total_price,line_items,created_at,billing_address,customer"
        }
        if after: params["created_at_min"] = after
        if before: params["created_at_max"] = before
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json().get('orders', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching orders: {e}")
            return []

    def get_sales_report(self, period="month"):
        """
        Calculates sales statistics for the given period.
        Currently supports 'month' (current calendar month).
        """
        now = get_now_hanoi()
        
        if period == "month":
            # First day of current month in Hanoi time
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            # Default to last 30 days if unknown
            from datetime import timedelta
            start_date = now - timedelta(days=30)
            
        endpoint = f"{self.shop_url}/admin/orders.json"
        all_orders = []
        page = 1
        limit = 50 # Haravan max for orders
        
        try:
            while True:
                params = {
                    "created_at_min": start_date.isoformat(),
                    "status": "any",
                    "fields": "total_price,created_at,email,cancelled_at",
                    "limit": limit,
                    "page": page
                }
                response = requests.get(endpoint, headers=self.headers, params=params)
                response.raise_for_status()
                orders = response.json().get('orders', [])
                if not orders: break
                
                all_orders.extend(orders)
                if len(orders) < limit: break
                page += 1
                if page > 100: break # Safety

            total_sales = 0
            valid_orders = []
            for order in all_orders:
                if order.get('cancelled_at') is None:
                    total_sales += float(order.get('total_price', 0))
                    valid_orders.append(order)
                
            return {
                "total_sales": total_sales,
                "total_orders": len(valid_orders),
                "total_customers": len(set(order.get('email') for order in valid_orders if order.get('email')))
            }
        except Exception as e:
            print(f"Haravan Sales Report Error: {e}")
            return {"total_sales": 0, "total_orders": 0, "total_customers": 0}

    def get_daily_revenue(self, period="month"):
        """
        Calculates revenue breakdown per day for the given period.
        """
        now = get_now_hanoi()
        if period == "month":
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            from datetime import timedelta
            start_date = now - timedelta(days=30)

        endpoint = f"{self.shop_url}/admin/orders.json"
        daily_data = {}
        page = 1
        limit = 50

        try:
            while True:
                params = {
                    "created_at_min": start_date.isoformat(),
                    "status": "any",
                    "fields": "total_price,created_at,cancelled_at",
                    "limit": limit,
                    "page": page
                }
                response = requests.get(endpoint, headers=self.headers, params=params)
                response.raise_for_status()
                orders = response.json().get('orders', [])
                if not orders: break

                for order in orders:
                    if order.get('cancelled_at') is None:
                        date_str = order.get('created_at', '').split('T')[0]
                        price = float(order.get('total_price', 0))
                        daily_data[date_str] = daily_data.get(date_str, 0) + price

                if len(orders) < limit: break
                page += 1
            return daily_data
        except Exception as e:
            print(f"Error getting daily revenue: {e}")
            return {}

    def get_product_revenue_ranking(self, days=30):
        """
        Ranks products by total revenue generated in the last X days.
        """
        from datetime import timedelta
        start_date = get_now_hanoi() - timedelta(days=days)
        endpoint = f"{self.shop_url}/admin/orders.json"
        product_revenue = {}
        page = 1
        limit = 50

        try:
            while True:
                params = {
                    "created_at_min": start_date.isoformat(),
                    "status": "any",
                    "fields": "line_items,cancelled_at",
                    "limit": limit,
                    "page": page
                }
                response = requests.get(endpoint, headers=self.headers, params=params)
                response.raise_for_status()
                orders = response.json().get('orders', [])
                if not orders: break

                for order in orders:
                    if order.get('cancelled_at') is None:
                        for item in order.get('line_items', []):
                            name = item.get('name')
                            # Revenue = price * qty (already discounted in line_item usually)
                            # Haravan line_item usually has 'price' and 'quantity'
                            revenue = float(item.get('price', 0)) * int(item.get('quantity', 1))
                            product_revenue[name] = product_revenue.get(name, 0) + revenue

                if len(orders) < limit: break
                page += 1
            
            # Sort by revenue
            sorted_ranking = sorted(product_revenue.items(), key=lambda x: x[1], reverse=True)
            return sorted_ranking
        except Exception as e:
            print(f"Error getting product ranking: {e}")
            return []

    def get_variant_sales(self, days=30):
        """
        Calculates the quantity sold for each variant in the last 'days'.
        Returns a dictionary mapping sku -> quantity_sold.
        """
        from datetime import timedelta
        start_date = get_now_hanoi() - timedelta(days=days)
        
        endpoint = f"{self.shop_url}/admin/orders.json"
        variant_sales = {}
        page = 1
        limit = 50
        
        try:
            while True:
                params = {
                    "created_at_min": start_date.isoformat(),
                    "status": "any",
                    "fields": "line_items",
                    "limit": limit,
                    "page": page
                }
                response = requests.get(endpoint, headers=self.headers, params=params)
                response.raise_for_status()
                orders = response.json().get('orders', [])
                if not orders: break
                
                for order in orders:
                    if order.get('cancelled_at') is None:
                        for item in order.get('line_items', []):
                            sku = item.get('sku')
                            if sku:
                                sku = str(sku).strip().upper()
                                qty = int(item.get('quantity', 0))
                                variant_sales[sku] = variant_sales.get(sku, 0) + qty
                
                if len(orders) < limit: break
                page += 1
                if page > 100: break # Safety
                
            return variant_sales
        except Exception as e:
            print(f"Haravan Variant Sales Error: {e}")
            return {}

    def search_order(self, query):
        """
        Search for an order by name (e.g., #1001) or email.
        """
        endpoint = f"{self.shop_url}/admin/orders.json"
        # If query starts with #, strip it
        name = query.replace("#", "")
        params = {
            "name": name,
            "status": "any",
             "fields": "id,name,email,status,financial_status,fulfillment_status,total_price,line_items,created_at"
        }
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            orders = response.json().get('orders', [])
            return orders
        except requests.exceptions.RequestException as e:
            print(f"Error searching order {query}: {e}")
            return []

    def get_order_by_id(self, order_id):
        """Get a single order by ID."""
        endpoint = f"{self.shop_url}/admin/orders/{order_id}.json"
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json().get('order')
        except requests.exceptions.RequestException as e:
            print(f"Error getting order {order_id}: {e}")
            return None

    def create_order(self, order_data):
        """Create a new order in Haravan."""
        endpoint = f"{self.shop_url}/admin/orders.json"
        payload = {"order": order_data}
        try:
            response = requests.post(endpoint, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json().get('order')
        except requests.exceptions.RequestException as e:
            print(f"Error creating order: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            return None

    def update_variant_price(self, variant_id: int, new_price: str) -> bool:
        """
        Update the price of a specific product variant on Haravan.
        Returns True on success, False on failure.
        """
        endpoint = f"{self.shop_url}/admin/variants/{variant_id}.json"
        payload = {"variant": {"id": variant_id, "price": new_price}}
        try:
            response = requests.put(endpoint, headers=self.headers, json=payload)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error updating variant {variant_id} price: {e}")
            return False

    def get_products_all(self):
        """
        Fetch all RAW products (not expanded to variants) for stale inventory scan.
        Returns a list of raw product dicts.
        """
        all_products = []
        page = 1
        while True:
            endpoint = f"{self.shop_url}/admin/products.json"
            params = {
                "limit": 250,
                "page": page,
                "fields": "id,title,variants,images,published_at"
            }
            try:
                response = requests.get(endpoint, headers=self.headers, params=params)
                response.raise_for_status()
                products = response.json().get('products', [])
                if not products:
                    break
                all_products.extend(products)
                page += 1
                if page > 200:
                    break
            except requests.exceptions.RequestException as e:
                print(f"Error fetching products page {page}: {e}")
                break
        return all_products

    def tag_product_tier(self, product_id: int, tier: int) -> bool:
        """
        Tags a product with its current pricing tier (1 or 2) on Haravan.
        Replaces any existing mecobooks-tier tag.
        Returns True on success.
        """
        new_tag = f"mecobooks-tier-{tier}"
        old_tag = f"mecobooks-tier-{2 if tier == 1 else 1}"

        # First fetch the product's existing tags
        endpoint = f"{self.shop_url}/admin/products/{product_id}.json"
        try:
            resp = requests.get(endpoint, headers=self.headers, params={"fields": "id,tags"})
            resp.raise_for_status()
            product = resp.json().get("product", {})
            existing_tags = [t.strip() for t in product.get("tags", "").split(",") if t.strip()]

            # Remove old tier tag, add new tier tag
            updated_tags = [t for t in existing_tags if t != old_tag]
            if new_tag not in updated_tags:
                updated_tags.append(new_tag)

            tags_str = ", ".join(updated_tags)
            payload = {"product": {"id": product_id, "tags": tags_str}}
            put_resp = requests.put(endpoint, headers=self.headers, json=payload)
            put_resp.raise_for_status()
            return True
        except Exception as e:
            print(f"Error tagging product {product_id} as {new_tag}: {e}")
            return False

    def create_product(self, title: str, body_html: str, price: str, sku: str, images: list = None, tags: str = "") -> dict:
        """
        Creates a new product on Haravan.
        Useful for creating automated bundles or special promotion items.
        Returns the created product data.
        """
        endpoint = f"{self.shop_url}/admin/products.json"
        
        payload = {
            "product": {
                "title": title,
                "body_html": body_html,
                "vendor": "Mecobooks",
                "product_type": "Combo",
                "tags": tags,
                "variants": [
                    {
                        "price": price,
                        "sku": sku,
                        "inventory_management": "haravan",
                        "inventory_policy": "deny",
                        "inventory_quantity": 1,
                        "requires_shipping": True,
                        "option1": "Default Title"
                    }
                ]
            }
        }
        
        if images:
            # Handle both URLs and base64 attachments
            payload["product"]["images"] = []
            for img in images:
                if isinstance(img, dict) and "attachment" in img:
                    payload["product"]["images"].append({
                        "attachment": img["attachment"],
                        "filename": "collage.jpg"
                    })
                else:
                    payload["product"]["images"].append({"src": img})

        try:
            resp = requests.post(endpoint, headers=self.headers, json=payload)
            resp.raise_for_status()
            return resp.json().get("product", {})
        except Exception as e:
            print(f"Error creating product '{title}': {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return {"error": str(e)}

if __name__ == "__main__":
    # Test the client
    client = HaravanClient()
    products = client.get_products(limit=2)
    print(f"Fetched {len(products)} products.")
    for p in products:
        data = client.extract_product_data(p)
        print(f"Product: {data.get('title')}")
        print(f"Images: {len(data.get('images'))}")
        print("-" * 20)
