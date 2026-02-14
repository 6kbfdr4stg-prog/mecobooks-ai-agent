from woocommerce import API
import json

URL = "https://mecobooks.com"
KEY = "ck_34f92dc77ecc6b196a6604fa29d9cf21cf3475c0"
SECRET = "cs_a03e99659fc6e5f837f7b8c8c70269e3fc99af60"

wcapi = API(
    url=URL,
    consumer_key=KEY,
    consumer_secret=SECRET,
    version="wc/v3",
    timeout=20
)

try:
    print("Fetching products...")
    products = wcapi.get("products", params={"per_page": 2}).json()
    
    if products:
        print(f"Found {len(products)} products.")
        for p in products:
            print(f"\nProduct: {p.get('name')}")
            print(f"Images raw data: {json.dumps(p.get('images'), indent=2)}")
            print(f"Meta Data keys: {[m['key'] for m in p.get('meta_data', [])]}")
            
            # Dump full meta data to see values
            print(json.dumps(p.get('meta_data', []), indent=2))

            if p.get("images") and len(p["images"]) > 0:
                print(f"First Image SRC: {p['images'][0].get('src')}")
            else:
                print("No images found in standard field.")
    else:
        print("No products returned.")
        print(products)

except Exception as e:
    print(f"Error: {e}")
