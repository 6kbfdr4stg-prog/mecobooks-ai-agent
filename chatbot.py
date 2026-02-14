from haravan_client import HaravanClient
from llm_service import LLMService
import json

class Chatbot:
    def __init__(self):
        self.haravan = HaravanClient()
        self.llm = LLMService()
        self.system_prompt = """
        Bạn là trợ lý ảo AI của "Tiệm Sách Anh Tuấn".
        Nhiệm vụ của bạn là hỗ trợ khách hàng tìm kiếm sách và kiểm tra đơn hàng.
        Luôn trả lời thân thiện, lịch sự và ngắn gọn bang Tiếng Việt.
        Nếu có thông tin sản phẩm, hãy hiển thị giá và mô tả ngắn gọn.
        """

    def determine_intent(self, message):
        """
        Determine user intent based on keywords.
        In a more advanced version, we would use the LLM to classify intent.
        """
        message = message.lower()
        if "tìm" in message or "giá" in message or "sách" in message or "mua" in message:
            return "search_product"
        if "đơn hàng" in message or "vận chuyển" in message or "ship" in message:
            return "check_order"
        return "general_chat"

    def process_message(self, user_message):
        intent = self.determine_intent(user_message)
        context_data = ""

        if intent == "search_product":
            # Extract basic query
            # Remove common keywords to get the actual product name
            # Clean query by removing common stop words
            stop_words = ["tìm", "kiếm", "mua", "giá", "sách", "cuốn", "quyển", "tập", "bộ", "của", "các", "những", "bao nhiêu", "là", "gì", "ở", "đâu"]
            clean_query = user_message.lower()
            for word in stop_words:
                clean_query = clean_query.replace(word, "")
            
            clean_query = clean_query.strip()
            
            # If query is empty after cleaning, use original or prompt user (using original for now)
            query_to_use = clean_query if clean_query else user_message

            products = self.haravan.search_products(query_to_use, limit=3)
            if products:
                # 1. Generate HTML for the user (Widget)
                product_html_list = []
                for p in products:
                    img_html = ""
                    if p.get('images'):
                        img_html = f'<img src="{p["images"][0]}" class="product-card-img" />'
                    
                    if len(desc) > 100:
                        desc = desc[:97] + "..."
                    
                    # Product Card HTML
                    card = f"<div style='margin-bottom: 20px; border: 1px solid #e0e0e0; border-radius: 8px; padding: 12px; background-color: #f9f9f9;'>"
                    card += f"<div style='font-size: 15px; font-weight: bold; margin-bottom: 4px;'>{p['title']}</div>"
                    card += f"<div style='color: #d32f2f; font-weight: bold; margin-bottom: 8px;'>{p['price']}₫</div>"
                    
                    if img_html:
                        card += f"<div style='margin-bottom: 8px;'>{img_html}</div>"
                        
                    card += f"<div style='font-size: 13px; color: #555; margin-bottom: 10px;'>{desc}</div>"
                    
                    # Links
                    links = []
                    if p.get('handle'):
                        links.append(f'<a href="https://mecobooks.com/products/{p["handle"]}" target="_blank" style="color: #0084ff; text-decoration: none; font-weight: 500;">🔗 Chi tiết</a>')
                    if p.get('variant_id'):
                        links.append(f'<a href="https://mecobooks.com/cart/{p["variant_id"]}:1" target="_blank" style="color: #d32f2f; font-weight: bold; text-decoration: none;">👉 Mua ngay</a>')
                    
                    if links:
                         card += "<div style='margin-top: 8px; padding-top: 8px; border-top: 1px dashed #ddd; display: flex; gap: 15px;'>" + "".join(links) + "</div>"
                    
                    card += "</div>"
                    product_html_list.append(card)
                
                final_html_output = "".join(product_html_list)

                # 2. Generate Text Context for LLM (so it knows what was returned)
                product_text_summary = "\n".join([f"- {p['title']} ({p['price']}d)" for p in products])
                context_data = f"Hệ thống đã tìm thấy các sản phẩm sau:\n{product_text_summary}"
                
                # 3. Get a short intro from LLM
                intro_prompt = f"""
                {self.system_prompt}
                Người dùng muốn tìm: "{query_to_use}"
                Hệ thống tìm thấy:
                {product_text_summary}
                
                Hãy viết một câu giới thiệu ngắn gọn, thân thiện (dưới 20 từ) để mời khách xem danh sách bên dưới. 
                Ví dụ: "Dạ, shop tìm thấy vài cuốn sách phù hợp với bạn ạ:"
                """
                llm_intro = self.llm.generate_response(intro_prompt)
                
                # 4. Combine Intro + HTML
                return f"{llm_intro}<br/><br/>{final_html_output}"

            else:
                context_data = f"Không tìm thấy sản phẩm nào phù hợp với từ khóa '{query_to_use}'."

        elif intent == "check_order":
            # Requires order ID or more info. For MVP, we'll list recent orders if no specific ID format found?
            # Or just tell LLM to ask for Order ID if not present.
            # Simplified: Fetch latest 3 orders to see if any match context (not secure for public, but ok for personal tool)
            orders = self.haravan.get_orders(limit=3)
            if orders:
                order_list = "\n".join([f"Mã đơn: {o.get('name')} - Trạng thái: {o.get('financial_status')}/{o.get('fulfillment_status')} - Tổng: {o.get('total_price')}" for o in orders])
                context_data = f"Thông tin các đơn hàng gần nhất (Admin View):\n{order_list}"
            else:
                context_data = "Không tìm thấy đơn hàng nào gần đây."
        
        # Construct Prompt
        full_prompt = f"""
        {self.system_prompt}
        
        Thông tin ngữ cảnh từ hệ thống Haravan:
        {context_data}

        Câu hỏi của người dùng: "{user_message}"
        
        Hãy trả lời người dùng dựa trên thông tin ngữ cảnh trên. Nếu không tìm thấy thông tin, hãy nói rõ.
        """
        
        response = self.llm.generate_response(full_prompt)
        if "429" in response:
             return "Hệ thống AI đang quá tải (Lỗi 429). Vui lòng đợi 30 giây rồi thử lại."
        return response

if __name__ == "__main__":
    bot = Chatbot()
    print("Bot: Xin chào! Tôi có thể giúp gì cho bạn?")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            break
        response = bot.process_message(user_input)
        print(f"Bot: {response}")
