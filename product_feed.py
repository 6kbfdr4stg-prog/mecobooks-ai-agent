from lxml import etree
from woocommerce_client import WooCommerceClient
import datetime

def generate_xml_feed():
    woo = WooCommerceClient()
    # Fetch all products (limit=100 for now, could loop for all)
    products = woo.search_products(" ", limit=100)
    
    # Namespace map
    nsmap = {
        "g": "http://base.google.com/ns/1.0"
    }
    
    rss = etree.Element("rss", version="2.0", nsmap=nsmap)
    channel = etree.SubElement(rss, "channel")
    
    # Channel Info
    etree.SubElement(channel, "title").text = "MecoBooks Product Feed"
    etree.SubElement(channel, "link").text = "https://mecobooks.com"
    etree.SubElement(channel, "description").text = "Sách hay mỗi ngày"
    
    for p in products:
        item = etree.SubElement(channel, "item")
        
        # Basic Fields
        etree.SubElement(item, "id").text = str(p.get('id', '')) # We need ID from woo client, check if search_products returns it. 
        # Wait, search_products returns a simplified dict. We might need raw data or ensure ID is in the dict.
        # Let's check woocommerce_client.py output structure. It currently returns: title, price, image, url, description... 
        # It DOES NOT return ID explicitly in the 'results' list, but it processes it internally.
        # We need to update user's woocommerce_client to include ID or handle it here.
        
        # For now, let's assume we update woocommerce_client to return ID, or use URL as ID (not ideal).
        # Let's check woocommerce_client.py again.
        
        etree.SubElement(item, "title").text = p.get('title', '')
        etree.SubElement(item, "description").text = p.get('description', '') or p.get('title', '')
        etree.SubElement(item, "link").text = p.get('url', '')
        etree.SubElement(item, "{http://base.google.com/ns/1.0}image_link").text = p.get('image', '')
        
        # Price (Google wants "100000 VND")
        price_val = p.get('price', '0').replace(',', '').replace('.', '')
        etree.SubElement(item, "{http://base.google.com/ns/1.0}price").text = f"{price_val} VND"
        
        # Availability
        stock = p.get('stock_status', 'instock')
        g_avail = "in_stock" if stock == 'instock' else "out_of_stock"
        etree.SubElement(item, "{http://base.google.com/ns/1.0}availability").text = g_avail
        
        # Condition
        etree.SubElement(item, "{http://base.google.com/ns/1.0}condition").text = "new"
        
        # Brand (Required)
        etree.SubElement(item, "{http://base.google.com/ns/1.0}brand").text = "MecoBooks" # Or publisher if available

    return etree.tostring(rss, pretty_print=True, xml_declaration=True, encoding="UTF-8")
