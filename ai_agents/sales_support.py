
import os
import sys

# Add parent dir to path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chatbot import Chatbot
from haravan_client import HaravanClient
from utils.logger import setup_logger

class SalesSupportAgent:
    def __init__(self):
        self.logger = setup_logger("sales_agent")
        self.bot = Chatbot()
        self.hrv = HaravanClient()
        self.conversations = {} # Store state per user_id
        
        # Load Knowledge Base
        try:
            with open("knowledge_base.txt", "r", encoding="utf-8") as f:
                self.knowledge_base = f.read()
        except FileNotFoundError:
            self.knowledge_base = "Chưa có thông tin cửa hàng."

    def _infer_author(self, book_title):
        """Ask LLM to identify the author of the book."""
        try:
            # Simple prompt to extract author
            prompt = f"Ai là tác giả của cuốn sách '{book_title}'? Chỉ trả về tên tác giả, không thêm nội dung nào khác. Nếu không biết hoặc không chắc, trả về 'Unknown'."
            author = self.bot.llm.generate_response(prompt).strip()
            
            # Basic validation
            if not author or "Unknown" in author or len(author) > 50 or "tác giả" in author.lower(): 
                return None
                
            print(f"🤖 AI Inferred Author for '{book_title}': {author}")
            self.logger.info(f"AI Inferred Author", extra={"metadata": {"book": book_title, "author": author}})
            return author.replace(".", "") # Clean up commonly added periods
        except Exception as e:
            print(f"Author Inference Error: {e}")
            self.logger.error("Author Inference Error", exc_info=True)
            return None

    def handle_customer_query(self, query, user_id="guest"):
        """
        Enhanced query handler with State Management for Order Collection.
        """
        print(f"🤖 [Sales Agent] Processing: '{query}' for User: {user_id}")
        self.logger.info(f"Processing Query", extra={"metadata": {"user_id": user_id, "query": query, "event": "USER_QUERY"}})
        
        # Initialize state if new user
        if user_id not in self.conversations:
            self.conversations[user_id] = {"state": "NORMAL", "data": {}}
            
        state = self.conversations[user_id]["state"]
        data = self.conversations[user_id]["data"]
        
        # --- STATE MACHINE ---
        
        if state == "COLLECTING_NAME":
            data["name"] = query
            self.conversations[user_id]["state"] = "COLLECTING_PHONE"
            return "Cảm ơn bạn. Cho mình xin số điện thoại để liên hệ giao hàng nhé!"
            
        # 1.5 STATE: TRACKING_ORDER
        elif state == "TRACKING_ORDER":
            import re
            # Extract number from query like "#123456" or "123456"
            # If user just says number, assume it's ID.
            # If user cancels, exit.
            
            if any(w in query.lower() for w in ["hủy", "không", "thôi"]):
                 self.conversations[user_id] = {"state": "NORMAL", "data": {}}
                 return "Dạ vâng, mình đã hủy tra cứu. Bạn cần hỗ trợ gì khác không ạ?"
            
            # Extract digits
            order_id = "".join(filter(str.isdigit, query))
            
            if not order_id:
                return "Mình chưa tìm thấy mã số nào trong tin nhắn. Bạn vui lòng nhập lại Mã đơn hàng (ví dụ: 25310) giúp mình nhé!"
            
            # Fetch Order
            order = self.hrv.get_order_by_id(order_id)
            if order:
                # Haravan statuses are complex. Using Financial + Fulfillment + Status
                status_v = order.get('status', 'unknown')
                fin_status = order.get('financial_status', 'unknown')
                ful_status = order.get('fulfillment_status', 'Chưa giao') or 'Chưa giao'
                
                status_map = {
                    "open": "Mở",
                    "closed": "Hoàn tất",
                    "cancelled": "Đã hủy",
                    "voided": "Vô hiệu",
                    "paid": "Đã thanh toán",
                    "pending": "Chờ thanh toán",
                    "fulfilled": "Đã giao hàng",
                    "null": "Chưa giao"
                }
                
                status_text = f"{status_map.get(status_v, status_v)} ({status_map.get(fin_status, fin_status)})"
                total = f"{int(float(order['total_price'])):,} VNĐ"
                
                # List items
                items_str = ", ".join([f"{item.get('title')} (x{item.get('quantity')})" for item in order['line_items']])
                
                response = f"""
                📦 **THÔNG TIN ĐƠN HÀNG #{order['id']}**
                - Trạng thái: **{status_vn}**
                - Tổng tiền: {total}
                - Sản phẩm: {items_str}
                """
                
                if order.get('financial_status') == 'pending':
                    response += "\n\n⚠️ Đơn hàng đang chờ thanh toán. Shop sẽ sớm liên hệ xác nhận ạ."
                elif order.get('status') == 'closed':
                    response += "\n\n✅ Đơn hàng đã hoàn tất! Cảm ơn bạn đã tin tưởng MecoBooks. ❤️"
                
                # Reset state
                self.conversations[user_id] = {"state": "NORMAL", "data": {}}
                
                self.logger.info(f"Bot Response (Order Info)", extra={"metadata": {"user_id": user_id, "response": response[:100], "order_id": order_id, "event": "BOT_RESPONSE"}})
                return response
            else:
                 msg = f"Hệ thống không tìm thấy đơn hàng mã #{order_id}. Bạn kiểm tra lại giúp mình xem có nhầm lẫn không nhé?"
                 self.logger.info(f"Bot Response (Order Not Found)", extra={"metadata": {"user_id": user_id, "response": msg, "event": "BOT_RESPONSE"}})
                 return msg

        # 2. STATE: COLLECTING_PHONE
        elif state == "COLLECTING_PHONE":
            import re
            phone = query.strip()
            # Simple validation
            if not re.match(r'^\d{9,11}$', phone):
                return "Số điện thoại có vẻ chưa đúng định dạng. Bạn vui lòng nhập lại nhé (chỉ gồm số)."
            
            data["phone"] = phone
            self.conversations[user_id]["state"] = "COLLECTING_ADDRESS"
            return "Tuyệt vời. Cuối cùng, bạn cho mình xin địa chỉ nhận hàng cụ thể (Số nhà, Đường, Phường/Xã, Quận/Huyện, Tỉnh/Thành) nha!"

        # 3. STATE: COLLECTING_ADDRESS
        elif state == "COLLECTING_ADDRESS":
            data["address"] = query
            self.conversations[user_id]["state"] = "CONFIRMING"
            
            # Summary
            product_name = data.get("product_name", "Sách")
            price_str = data.get("price", "0").replace(",", "").replace(".", "")
            try:
                price_val = int(price_str)
            except Exception as e:                price_val = 0
                
            # Shipping Logic
            shipping_fee = 20000
            if price_val >= 300000:
                shipping_fee = 0
                
            total_val = price_val + shipping_fee
            
            # Save for next step
            data["shipping_fee"] = shipping_fee
            data["total"] = total_val
            
            shipping_text = f"{shipping_fee:,} VNĐ" if shipping_fee > 0 else "Miễn phí"
            total_text = f"{total_val:,} VNĐ"
            
            return f"""
            🔔 XÁC NHẬN ĐƠN HÀNG:
            - Sách: {product_name}
            - Giá: {data.get("price", "0")} VNĐ
            - Phí ship: {shipping_text}
            - TỔNG CỘNG: {total_text}
            -------------------------
            - Họ tên: {data.get('name')}
            - SĐT: {data.get('phone')}
            - Địa chỉ: {data.get('address')}
            
            Bạn có muốn "Xác nhận đặt hàng" ngay không? (Trả lời "Có" hoặc "Ok")
            """

        # 4. STATE: CONFIRMING
        elif state == "CONFIRMING":
            if any(w in query.lower() for w in ["có", "ok", "đúng", "chốt", "xác nhận", "đồng ý"]):
                # Create Order
                shipping_cost = str(data.get("shipping_fee", 20000))
                
                order_data = {
                    "email": "guest@example.com",
                    "send_receipt": True,
                    "financial_status": "pending",
                    "fulfillment_status": None,
                    "customer": {
                        "first_name": data["name"],
                        "last_name": "",
                        "email": "guest@example.com"
                    },
                    "billing_address": {
                        "first_name": data["name"],
                        "last_name": "",
                        "address1": data["address"],
                        "phone": data["phone"],
                        "city": "Hồ Chí Minh", # Default or fallback
                        "country": "Vietnam"
                    },
                    "shipping_address": {
                        "first_name": data["name"],
                        "last_name": "",
                        "address1": data["address"],
                        "phone": data["phone"],
                        "city": "Hồ Chí Minh",
                        "country": "Vietnam"
                    },
                    "line_items": [
                        {
                            "variant_id": int(data.get("variant_id")),
                            "quantity": 1
                        }
                    ],
                    "shipping_lines": [
                        {
                            "code": "Flat Rate",
                            "price": int(data.get("shipping_fee", 20000)),
                            "title": "Phí vận chuyển"
                        }
                    ]
                }
                
                print(f"📦 Creating Haravan Order: {order_data}")
                new_order = self.hrv.create_order(order_data)
                
                if new_order:
                    # Log Conversion
                    self.logger.info(f"Order Created", extra={"metadata": {"user_id": user_id, "order_id": new_order['id'], "total": order_data.get('shipping_lines')[0]['total'], "event": "CONVERSION"}})
                    # Reset State
                    self.conversations[user_id] = {"state": "NORMAL", "data": {}}
                    
                    base_msg = f"🎉 Đặt hàng thành công! Mã đơn hàng của bạn là #{new_order['id']}. Shop sẽ sớm liên hệ xác nhận ạ. Cảm ơn bạn đã ủng hộ Tiệm Sách Anh Tuấn!"
                    
                    # --- UPSELL LOGIC (Proactive Selling) ---
                    try:
                        import random
                        # Get Best Sellers (Using popular products or just some products for now)
                        best_sellers = self.hrv.get_products(limit=5)
                        if best_sellers:
                            # Filter out the book just bought
                            current_variant_id = int(data.get("variant_id", 0))
                            recommendations = [p for p in best_sellers if p['variant_id'] != current_variant_id]
                            
                            if recommendations:
                                rec_product = random.choice(recommendations)
                                upsell_msg = f"\n\n💡 GỢI Ý: Shop thấy bạn đọc cuốn này chắc cũng sẽ thích **'{rec_product.get('name')}'** đó ạ. Sách này đang được rất nhiều bạn tìm mua. Bạn có muốn xem thử không?"
                                return base_msg + upsell_msg
                    except Exception as e:
                        print(f"Upsell Error: {e}")
                        
                    return base_msg
                else:
                    self.conversations[user_id]["state"] = "NORMAL" # Reset on error to avoid loop
                    return "Xin lỗi, hệ thống gặp sự cố khi tạo đơn hàng. Bạn vui lòng nhắn tin qua Zalo hoặc Fanpage để được hỗ trợ thủ công ạ."
            else:
                # Cancel
                self.conversations[user_id] = {"state": "NORMAL", "data": {}}
                return "Đã hủy thao tác đặt hàng. Bạn cần tìm thêm sách gì không?"

        # --- NORMAL FLOW (Intent Detection) ---
        
        query_lower = query.lower()
        
        # Detect Buy Intent explicitly
        buy_keywords = ["mua sách", "đặt hàng", "lấy cuốn này", "chốt đơn", "mua cuốn này", "ship cho mình"]
        if any(w in query_lower for w in buy_keywords):
             # Try to infer product from context if "cuốn này"
             # For MVP, user usually says "Mua cuốn Nhà Giả Kim"
             # Let's verify we have a product context or search for it.
             
             # If "cuốn này", check if we discussed a product recently? 
             # (Simple MVP: Ask user which book if not clear)
             
             # Let's try to extract product name from the buy command, e.g. "Mua sách Nhà Giả Kim"
             # If just "Mua sách", ask "Bạn muốn mua sách nào ạ?"
             
             target_book = query
             for w in buy_keywords:
                 target_book = target_book.replace(w, "", 1) # simple strip
             target_book = target_book.strip()
             
             if len(target_book) < 2:
                 return "Bạn muốn mua sách nào ạ? (Ví dụ: Mua sách Nhà Giả Kim)"
            
             # Search with fallback
             products = self.hrv.search_products(target_book, limit=1)
             
             if products:
                 product = products[0]
                 # Log successful search
                 self.logger.info(f"Product Found", extra={"metadata": {"query": target_book, "product": product.get('title')}})
                 # Start collecting info
                 self.conversations[user_id]["state"] = "COLLECTING_NAME"
                 self.conversations[user_id]["data"] = {
                     "variant_id": product.get('variant_id'),
                     "product_name": product.get('title'),
                     "price": product.get('price')
                 }
                 return f"Bạn muốn đặt cuốn '{product.get('title')}' ({product.get('price')}đ) đúng không ạ?\nCho mình xin Tên của bạn để tiện xưng hô nhé!"
             else:
                 return "Hiện tại mình chưa tìm thấy cuốn sách đó. Bạn kiểm tra lại tên sách giúp mình nhé."
        
        # Detect Tracking Intent
        tracking_keywords = ["kiểm tra đơn", "tra cứu đơn", "bao giờ có hàng", "đơn hàng của tôi", "xem đơn hàng", "tình trạng đơn"]
        if any(w in query_lower for w in tracking_keywords):
            self.conversations[user_id]["state"] = "TRACKING_ORDER"
            return "Dạ bạn cho mình xin Mã đơn hàng (ví dụ: #12345) để mình kiểm tra ngay nhé!"

        # Standard Consulting Flow (Existing Logic)
        intent_check = ["có sách", "còn sách", "tìm sách", "giá sách", "mua sách", "tìm cuốn", "có cuốn", "tìm quyển", "có quyển", "tư vấn", "hỏi về"]
        if any(phrase in query.lower() for phrase in intent_check):
            # Search
            products = self.hrv.search_products(query, limit=5)
            
            if products:
                # Return structured data
                return {
                    "type": "product_list",
                    "text": f"Dạ, mình tìm thấy {len(products)} cuốn sách phù hợp với yêu cầu của bạn nè:",
                    "products": products
                }
            else:
                # If local search fails, ask LLM to chat nicely or fallback
                # For now, just return text
                response = self.bot.llm.generate_response(f"Khách hỏi: '{query}'. Khách hỏi về sách nhưng hệ thống tìm không thấy. Hãy xin lỗi và gợi ý họ nhắn tin Zalo để admin kiểm tra kỹ hơn.")
                return {"type": "text", "text": response}
        
        # Default chat
        res = self.bot.process_message(query)
        # Check if LLM response looks like a product list? No, explicit search is better.
        return {"type": "text", "text": res}

    def process_message(self, message, platform="web", image_url=None, image_data=None, user_id="guest"):
        """
        Wrapper to be compatible with server.py's expected interface.
        """
        if image_url or image_data:
            return self.bot.process_message(message, platform, image_url, image_data)
        
        # Get structured response
        response_data = self.handle_customer_query(message, user_id=user_id)
        
        # If string (legacy or simple return), wrap it
        if isinstance(response_data, str):
            response_data = {"type": "text", "text": response_data}
            
        # Format for Platform
        if platform == "web":
            # Convert to HTML for the widget
            if response_data.get("type") == "product_list":
                html = f"<div class='h-bot-message' style='margin-bottom:10px;'>{response_data.get('text')}</div>"
                html += "<div class='h-product-list' style='display:flex; flex-direction:column; gap:10px;'>"
                
                for p in response_data.get('products'):
                    img = p.get('image', 'https://via.placeholder.com/150')
                    price = p.get('price', 'Liên hệ')
                    if price != "Liên hệ": price += "₫"
                    title = p.get('title', 'Sản phẩm')
                    link = p.get('url', '#')
                    
                    html += f"""
                    <div class="h-product-row" style="display:flex; border:1px solid #eee; border-radius:8px; overflow:hidden; background:#fff; padding:8px; align-items:center; gap:10px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                        <div style="width:70px; height:70px; flex-shrink:0; background:#f9f9f9; border-radius:4px; overflow:hidden; display:flex; align-items:center; justify-content:center;">
                            <img src="{img}" style="max-width:100%; max-height:100%; object-fit:contain;">
                        </div>
                        <div style="flex:1; min-width:0;">
                            <div style="font-weight:600; font-size:13px; margin-bottom:2px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; color:#333;">{title}</div>
                            <div style="color:#d32f2f; font-weight:bold; font-size:14px; margin-bottom:6px;">{price}</div>
                            <a href="{link}" target="_blank" style="display:inline-block; background:#0084ff; color:white; padding:3px 10px; border-radius:4px; text-decoration:none; font-size:11px; font-weight:500;">Xem chi tiết</a>
                        </div>
                    </div>
                    """
                html += "</div>"
                return html
            else:
                return response_data["text"]

        elif platform == "facebook":
            # Convert to Generic Template
            if response_data.get("type") == "product_list":
                elements = []
                for p in response_data.get('products')[:10]: # FB limit 10
                    img = p.get('image', '')
                    price = p.get('price', 'Liên hệ')
                    if price != "Liên hệ": price += "₫"
                    
                    elements.append({
                        "title": p.get('title', 'Sản phẩm'),
                        "image_url": img,
                        "subtitle": f"Giá: {price}",
                        "default_action": {
                            "type": "web_url",
                            "url": p.get('url', '#'),
                            "webview_height_ratio": "tall",
                        },
                        "buttons": [
                            {
                                "type": "web_url",
                                "url": p.get('url', '#'),
                                "title": "Xem trên Web"
                            },
                             {
                                "type": "postback",
                                "title": "Mua ngay",
                                "payload": f"BUY_{p.get('id', '0')}"
                            }
                        ]
                    })
                return elements # create_server will wrap this in attachment
            else:
                return response_data["text"]
        
        return response_data["text"]

if __name__ == "__main__":
    agent = SalesSupportAgent()
    print(agent.handle_customer_query("Bạn có sách Nhà Giả Kim không?"))
