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
        """Fetch a list of products from Haravan."""
        endpoint = f"{self.shop_url}/admin/products.json"
        params = {
            "limit": limit,
            "page": page,
            "fields": "id,title,body_html,images,variants,sku"
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            products = response.json().get('products', [])
            return [self.extract_product_data(p) for p in products]
        except requests.exceptions.RequestException as e:
            print(f"Error fetching products: {e}")
            return []

    def extract_product_data(self, product):
        """Extract relevant data for video generation from a product object."""
        
        # Get Images (limiting to top 10 as per video generator spec)
        images = [img['src'] for img in product.get('images', [])][:10]
        
        # Get Price and Variant ID (from first variant)
        price = 0
        variant_id = None
        if product.get('variants'):
            variant = product['variants'][0]
            price = variant.get('price', 0)
            variant_id = variant.get('id')
            sku = variant.get('sku')
            inventory_qty = variant.get('inventory_quantity', 0)
            
        # Clean description (simple strip for now, might need HTML parsing later)
        description = product.get('body_html', '')
        # Basic HTML tag strip could be added here if needed
        
        return {
            "id": product.get('id'),
            "title": product.get('title'),
            "description": description,
            "price": price,
            "variant_id": variant_id,
            "sku": sku,
            "inventory_quantity": inventory_qty,
            "handle": product.get('handle'),
            "images": images
        }

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

    def search_order(self, query):
        """
        Search for an order by name (e.g., #1001) or email.
        Note: Haravan/Shopify API search is limited. 
        We'll try to use the 'name' filter if it looks like an order number,
        otherwise we might need to list and filter (inefficient) or use search endpoint if available.
        For now, let's assume query is Order Name (e.g. '1001')
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
