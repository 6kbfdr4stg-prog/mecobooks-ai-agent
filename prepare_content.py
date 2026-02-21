import os
import requests
import re
from slugify import slugify
from haravan_client import HaravanClient
from config import TEMP_IMAGE_DIR

# Ensure temp directory exists
os.makedirs(TEMP_IMAGE_DIR, exist_ok=True)

def clean_html(raw_html):
    """Remove HTML tags from a string."""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()

def download_image(url, save_dir, prefix):
    """Download an image from a URL."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Extract extension or default to .jpg
        ext = os.path.splitext(url)[1].split('?')[0]
        if not ext:
            ext = ".jpg"
            
        filename = f"{prefix}_{slugify(url.split('/')[-1])[:50]}{ext}"
        filepath = os.path.join(save_dir, filename)
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return filepath
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return None

def prepare_product_content(product_data):
    """
    Prepare product data for video generation.
    - Cleans description.
    - Downloads images.
    - Formats data into a standardized dictionary.
    """
    print(f"Preparing content for: {product_data.get('title')}")
    
    # 1. Clean Text
    bs_description = clean_html(product_data.get('description'))
    # formatting price
    price_formatted = "{:,.0f} đ".format(float(product_data.get('price'))) if product_data.get('price') else ""
    
    # Create a simple script if description is too short or empty
    if len(bs_description) < 50:
        script = f"Giới thiệu sản phẩm mới: {product_data.get('title')}. Giá bán hấp dẫn chỉ {price_formatted}. Mua ngay rại cửa hàng của chúng tôi."
    else:
        # Take first 300 chars or so for video to not be too long? 
        # For now, let's use the full description but maybe truncate later
        script = bs_description

    # 2. Download Images
    local_images = []
    pid = product_data.get('id')
    for idx, img_url in enumerate(product_data.get('images')):
        prefix = f"{pid}_{idx}"
        local_path = download_image(img_url, TEMP_IMAGE_DIR, prefix)
        if local_path:
            local_images.append(local_path)
    
    return {
        "id": pid,
        "title": product_data.get('title'),
        "script": script,
        "price_text": price_formatted,
        "images": local_images
    }

if __name__ == "__main__":
    client = HaravanClient()
    products = client.get_products(limit=1)
    if products:
        p_data = client.extract_product_data(products[0])
        content = prepare_product_content(p_data)
        print("Content Prepared:")
        print(f"Title: {content['title']}")
        print(f"Script (first 100 chars): {content['script'][:100]}...")
        print(f"Images downloaded: {len(content['images'])}")
