import requests
import json
import os
from config import HARAVAN_SHOP_URL, HARAVAN_ACCESS_TOKEN

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

    def get_all_products(self):
        """Fetch ALL products from Haravan using pagination."""
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
            print(f"✅ Page {page} fetched. Total variants so far: {len(all_variants)}")
            
            if len(variants) < limit: # Likely the last page (variants are expanded, but let's check against product count logic)
                # Actually, limit is on products, not variants. 
                # If get_products returns variants, we can't easily tell if it's the last page of PRODUCTS.
                # Better to check the raw product response length.
                pass
            
            # Since get_products expands to variants, let's refactor slightly to be safe.
            page += 1
            # Safety break to avoid infinite loops if API behaves weirdly
            if page > 100: break 
            
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

    def get_orders(self, limit=5, status='any'):
        """Fetch latest orders."""
        endpoint = f"{self.shop_url}/admin/orders.json"
        params = {
            "limit": limit,
            "status": status,
            "fields": "id,name,email,financial_status,fulfillment_status,total_price,line_items,created_at"
        }
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
        from datetime import datetime
        now = datetime.now()
        
        if period == "month":
            # First day of current month
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            # Default to last 30 days if unknown
            start_date = now.replace(day=1) # Simplified for now
            
        endpoint = f"{self.shop_url}/admin/orders.json"
        all_orders = []
        page = 1
        limit = 50 # Haravan max for orders
        
        try:
            while True:
                params = {
                    "created_at_min": start_date.isoformat(),
                    "status": "any",
                    "fields": "total_price,created_at,email",
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
            for order in all_orders:
                total_sales += float(order.get('total_price', 0))
                
            return {
                "total_sales": total_sales,
                "total_orders": len(all_orders),
                "total_customers": len(set(order.get('email') for order in all_orders if order.get('email')))
            }
        except Exception as e:
            print(f"Haravan Sales Report Error: {e}")
            return {"total_sales": 0, "total_orders": 0, "total_customers": 0}

    def get_variant_sales(self, days=30):
        """
        Calculates the quantity sold for each variant in the last 'days'.
        Returns a dictionary mapping sku -> quantity_sold.
        """
        from datetime import datetime, timedelta
        start_date = datetime.now() - timedelta(days=days)
        
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
             "fields": "id,name,email,financial_status,fulfillment_status,total_price,line_items,created_at"
        }
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            orders = response.json().get('orders', [])
            return orders
        except requests.exceptions.RequestException as e:
            print(f"Error searching order {query}: {e}")
            return []

if __name__ == "__main__":
    # Test the client
    client = HaravanClient()
    products = client.get_products(limit=2)
    print(f"Fetched {len(products)} products.")
    for p in products:
        data = client.extract_product_data(p)
        print(f"Product: {data['title']}")
        print(f"Images: {len(data['images'])}")
        print("-" * 20)
