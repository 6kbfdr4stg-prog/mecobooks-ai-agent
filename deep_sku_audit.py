import json
from haravan_client import HaravanClient
from woocommerce_client import WooCommerceClient

h = HaravanClient()
w = WooCommerceClient()

print("🔍 Đang lấy dữ liệu từ Haravan (50 sản phẩm)...")
h_variants = h.get_products(limit=50) # This now returns expanded variants
h_skus = {v['sku']: v for v in h_variants if v.get('sku')}
print(f"✅ Đã lấy {len(h_variants)} variants từ Haravan. SKUs ảo ví dụ: {list(h_skus.keys())[:5]}")

print("\n🔍 Đang lấy dữ liệu từ WooCommerce...")
# WooCommerce limits per_page to 100
w_inventory_list = w.get_all_inventory(limit=100)
if not w_inventory_list:
    # Let's try to get raw products to see why it's empty
    try:
        raw = w.wcapi.get("products", params={"per_page": 10, "status": "publish"}).json()
        print(f"Raw WooCommerce Response Snippet: {str(raw)[:500]}")
    except Exception as e:
        print(f"Error getting raw response: {e}")

w_skus = {item['sku']: item for item in w_inventory_list if item.get('sku')}
print(f"✅ Đã lấy {len(w_inventory_list)} sản phẩm từ WooCommerce. SKUs ví dụ: {list(w_skus.keys())[:5]}")

intersection = set(h_skus.keys()).intersection(set(w_skus.keys()))
print(f"\n--- KẾT QUẢ SO KHỚP ---")
print(f"Số lượng SKU trùng khớp: {len(intersection)}")

if intersection:
    print(f"Mẫu sản phẩm khớp:")
    for sku in list(intersection)[:5]:
        h_data = h_skus[sku]
        w_data = w_skus[sku]
        print(f"SKU: {sku} | Haravan: {h_data.get('qty')} | Woo: {w_data.get('stock_quantity')} | Name: {w_data.get('name')}")
else:
    print("❌ Không tìm thấy SKU trùng khớp nào trong 250 sản phẩm WooCommerce đầu tiên.")
    
    # Debug: Check if Product IDs match at least
    print("\n--- PHÂN TÍCH SKU PATTERN ---")
    if w_skus:
        sample_w_sku = list(w_skus.keys())[0]
        print(f"Mẫu SKU Woo: {sample_w_sku}")
        parts = sample_w_sku.split('-')
        if len(parts) >= 3 and parts[0] == 'HRV':
            p_id = parts[1]
            v_id = parts[2]
            print(f"Trích xuất: Product ID={p_id}, Variant ID={v_id}")
            
            # Check if this Product ID exists in Haravan
            print(f"Đang kiểm tra Product ID {p_id} trên Haravan...")
            try:
                # Need raw access to check ID
                raw_url = f"https://{h.shop_url}/admin/products/{p_id}.json"
                import requests
                headers = {"Authorization": f"Bearer {h.access_token}"}
                resp = requests.get(raw_url, headers=headers)
                if resp.status_code == 200:
                    data = resp.json().get('product', {})
                    print(f"✅ Tìm thấy Product ID {p_id} trên Haravan: {data.get('title')}")
                    # Check variants
                    h_v_ids = [str(v['id']) for v in data.get('variants', [])]
                    print(f"Các Variant IDs trong Haravan: {h_v_ids}")
                    if v_id in h_v_ids:
                        print(f"✅ Variant ID {v_id} CŨNG KHỚP!")
                    else:
                        print(f"❌ Variant ID {v_id} KHÔNG khớp với bất kỳ variant nào của Haravan!")
                else:
                    print(f"❌ Không tìm thấy Product ID {p_id} trên Haravan (Status: {resp.status_code})")
            except Exception as e:
                print(f"Error checking Haravan: {e}")
