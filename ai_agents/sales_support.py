
import os
import sys

# Add parent dir to path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chatbot import Chatbot
from woocommerce_client import WooCommerceClient

class SalesSupportAgent:
    def __init__(self):
        self.bot = Chatbot()
        self.woo = WooCommerceClient()
        self.conversations = {} # Store state per user_id

    def handle_customer_query(self, query, user_id="guest"):
        """
        Enhanced query handler with State Management for Order Collection.
        """
        print(f"🤖 [Sales Agent] Processing: '{query}' for User: {user_id}")
        
        # Initialize state if new user
        if user_id not in self.conversations:
            self.conversations[user_id] = {"state": "NORMAL", "data": {}}
            
        state = self.conversations[user_id]["state"]
        data = self.conversations[user_id]["data"]
        
        # --- STATE MACHINE ---
        
        # 1. STATE: COLLECTING_NAME
        if state == "COLLECTING_NAME":
            data["name"] = query
            self.conversations[user_id]["state"] = "COLLECTING_PHONE"
            return "Cảm ơn bạn. Cho mình xin số điện thoại để liên hệ giao hàng nhé!"
            
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
            price = data.get("price", "0")
            total = price 
            
            return f"""
            🔔 XÁC NHẬN ĐƠN HÀNG:
            - Sách: {product_name}
            - Giá: {price} VNĐ (Chưa bao gồm phí ship)
            - Họ tên: {data['name']}
            - SĐT: {data['phone']}
            - Địa chỉ: {data['address']}
            
            Bạn có muốn "Xác nhận đặt hàng" ngay không? (Trả lời "Có" hoặc "Ok")
            """

        # 4. STATE: CONFIRMING
        elif state == "CONFIRMING":
            if any(w in query.lower() for w in ["có", "ok", "đúng", "chốt", "xác nhận", "đồng ý"]):
                # Create Order
                order_data = {
                    "payment_method": "cod",
                    "payment_method_title": "Cash on Delivery",
                    "set_paid": False,
                    "billing": {
                        "first_name": data["name"],
                        "address_1": data["address"],
                        "city": "", # Simplify
                        "state": "",
                        "postcode": "",
                        "country": "VN",
                        "email": "guest@example.com",
                        "phone": data["phone"]
                    },
                    "shipping": {
                        "first_name": data["name"],
                        "address_1": data["address"],
                        "city": "",
                        "state": "",
                        "postcode": "",
                        "country": "VN"
                    },
                    "line_items": [
                        {
                            "product_id": data.get("product_id"),
                            "quantity": 1
                        }
                    ]
                }
                
                print(f"📦 Creating Order: {order_data}")
                new_order = self.woo.create_order(order_data)
                
                if new_order:
                    # Reset State
                    self.conversations[user_id] = {"state": "NORMAL", "data": {}}
                    return f"🎉 Đặt hàng thành công! Mã đơn hàng của bạn là #{new_order['id']}. Shop sẽ sớm liên hệ xác nhận ạ. Cảm ơn bạn đã ủng hộ Tiệm Sách Anh Tuấn!"
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
            
             # Search to get ID
             products = self.woo.search_products(target_book, limit=1)
             if products:
                 product = products[0]
                 # Start collecting info
                 self.conversations[user_id]["state"] = "COLLECTING_NAME"
                 self.conversations[user_id]["data"] = {
                     "product_id": product['id'],
                     "product_name": product['title'],
                     "price": product['price']
                 }
                 return f"Bạn muốn đặt cuốn '{product['title']}' ({product['price']}đ) đúng không ạ?\nCho mình xin Tên của bạn để tiện xưng hô nhé!"
             else:
                 return "Hiện tại mình chưa tìm thấy cuốn sách đó. Bạn kiểm tra lại tên sách giúp mình nhé."
        
        # Standard Consulting Flow (Existing Logic)
        intent_check = ["có sách", "còn sách", "tìm sách", "giá sách", "mua sách"]
        if any(phrase in query.lower() for phrase in intent_check):
            # Extract potential book name (naive approach)
            # Better approach: asking LLM to extract entity
            products = self.woo.search_products(query, limit=3)
            
            if products:
                # Context injection
                product_context = "Thông tin sách tìm được:\n"
                for p in products:
                    product_context += f"- {p['title']}: {p['price']} VNĐ ({p['inventory_text']}) - Link: {p['url']}\n"
                
                system_instruction = "Bạn là nhân viên tư vấn của Tiệm Sách Anh Tuấn. Hãy trả lời khách dựa trên thông tin sách tìm được dưới đây. Khéo léo chốt đơn."
                full_prompt = f"{system_instruction}\n\n{product_context}\n\nKhách hỏi: {query}"
                response = self.bot.llm.generate_response(full_prompt)
                return response
            else:
                return self.bot.llm.generate_response(f"Khách hỏi: '{query}'. Khách hỏi về sách nhưng hệ thống tìm không thấy. Hãy xin lỗi và gợi ý họ nhắn tin Zalo để admin kiểm tra kỹ hơn.")
        
        # Default chat
        # If not a specific sales query, fall back to standard chatbot processing
        # But Chatbot.process_message handles everything including intent.
        # So we might just want to return self.bot.process_message(query)
        return self.bot.process_message(query)

    def process_message(self, message, platform="web", image_url=None, image_data=None, user_id="guest"):
        """
        Wrapper to be compatible with server.py's expected interface.
        Delegates to handle_customer_query for text-only messages on web/fb.
        Hand off to internal bot for complex image handling if needed,
        or just integrate logic here.
        """
        # If there are images, we might want to bypass the simple sales logic 
        # or pass it through. For now, let's use the internal bot's robust process_message
        # if there are images, otherwise use our enhanced handler.
        
        if image_url or image_data:
            return self.bot.process_message(message, platform, image_url, image_data)
        
        # For text only, use our enhanced logic
        # Note: handle_customer_query currently returns a string.
        # server.py expects string or structured data (for FB).
        # Our handle_customer_query logic mainly returns strings (via self.bot.chat)
        # We should ensure return types align.
        
        return self.handle_customer_query(message, user_id=user_id)

if __name__ == "__main__":
    agent = SalesSupportAgent()
    print(agent.handle_customer_query("Bạn có sách Nhà Giả Kim không?"))
