# from haravan_client import HaravanClient
from woocommerce_client import WooCommerceClient
from llm_service import LLMService
import json

class Chatbot:
    def __init__(self):
        # self.haravan = HaravanClient()
        self.woo = WooCommerceClient()
        self.llm = LLMService()
        # Load Knowledge Base
        try:
            with open("knowledge_base.txt", "r", encoding="utf-8") as f:
                self.knowledge_base = f.read()
        except FileNotFoundError:
            self.knowledge_base = "Chưa có thông tin cửa hàng."

        self.system_prompt = f"""
        Bạn là trợ lý ảo AI của "Tiệm Sách Anh Tuấn".
        Nhiệm vụ của bạn là hỗ trợ khách hàng tìm kiếm sách, kiểm tra đơn hàng và giải đáp thắc mắc.
        
        THÔNG TIN CỬA HÀNG & CHÍNH SÁCH:
        {self.knowledge_base}
        
        HƯỚNG DẪN TRẢ LỜI:
        1. Luôn thân thiện, lịch sự, xưng "mình" hoặc "shop".
        2. Nếu khách hỏi thông tin có trong phần CHÍNH SÁCH, hãy trả lời chính xác theo đó.
        3. Nếu khách tìm sách, hãy hiển thị giá và mô tả ngắn gọn nếu có.
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

    def process_message(self, user_message, platform="web", image_url=None, image_data=None):
        import requests
        from PIL import Image
        from io import BytesIO

        intent = "general_chat"
        
        # 0. Handle Image Input first (Visual Search)
        img = None
        if image_url:
            intent = "search_product"
            # Download image
            try:
                print(f"Downloading image from: {image_url}")
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                img_response = requests.get(image_url, headers=headers)
                img = Image.open(BytesIO(img_response.content))
            except Exception as e:
                print(f"Image processing error: {e}")
                return "Xin lỗi, mình không đọc được ảnh này. Bạn thử nhập tên sách giúp mình nhé!"
        
        elif image_data:
             intent = "search_product"
             try:
                 print("Processing uploaded image bytes...")
                 img = Image.open(BytesIO(image_data))
             except Exception as e:
                 print(f"Image bytes processing error: {e}")
                 return "Xin lỗi, ảnh tải lên bị lỗi. Bạn thử lại nhé!"

        if img:
            try:
                # Ask LLM to identify the book
                vision_prompt = """
                Hãy nhìn vào bức ảnh này và xác định tên cuốn sách và tác giả (nếu có).
                Chỉ trả về Tên Sách + Tác Giả. Không cần giải thích thêm.
                Ví dụ: "Nhà Giả Kim - Paulo Coelho"
                """
                
                recognized_text = self.llm.generate_response(vision_prompt, image_data=img)
                print(f"AI recognized: {recognized_text}")
                
                # Use the recognized text as the search query
                user_message = recognized_text.strip()
            except Exception as e:
                 print(f"LLM Vision Error: {e}")
                 return "Xin lỗi, mình chưa nhận diện được sách trong ảnh."

        if not image_url and not image_data:
            intent = self.determine_intent(user_message)
        
        context_data = ""

        if intent == "search_product":
            # Extract basic query
            # Remove common keywords to get the actual product name
            stop_words = ["tìm", "kiếm", "mua", "giá", "sách", "cuốn", "quyển", "tập", "bộ", "của", "các", "những", "bao nhiêu", "là", "gì", "ở", "đâu"]
            clean_query = user_message.lower()
            for word in stop_words:
                clean_query = clean_query.replace(word, "")
            
            clean_query = clean_query.strip()
            query_to_use = clean_query if clean_query else user_message

            # Search products using WooCommerce
            products = self.woo.search_products(query_to_use, limit=5)
            if products:
                if platform == "facebook":
                    # Return list of elements for Generic Template
                    elements = []
                    for p in products:
                        element = {
                            "title": p['title'],
                            "subtitle": f"{p['price']} VND",
                            "image_url": p['image'],
                            "buttons": [
                                {
                                    "type": "web_url",
                                    "url": p['url'],
                                    "title": "Xem chi tiết"
                                },
                                {
                                    "type": "web_url",
                                    "url": p['url'], # Direct to product page for now as add-to-cart link format differs
                                    "title": "Mua ngay"
                                }
                            ]
                        }
                        elements.append(element)
                    return elements

                # 1. Generate HTML for the user (Widget)
                product_html_list = []
                for p in products[:3]: # Limit to 3 for web widget
                    img_html = ""
                    if p.get('image'):
                        img_html = f'<img src="{p["image"]}" class="product-card-img" />'
                    
                    desc = p.get('description', '')
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
                    links.append(f'<a href="{p["url"]}" target="_blank" style="color: #0084ff; text-decoration: none; font-weight: 500;">🔗 Chi tiết</a>')
                    links.append(f'<a href="{p["url"]}" target="_blank" style="color: #d32f2f; font-weight: bold; text-decoration: none;">👉 Mua ngay</a>')
                    
                    if links:
                         card += "<div style='margin-top: 8px; padding-top: 8px; border-top: 1px dashed #ddd; display: flex; gap: 15px;'>" + "".join(links) + "</div>"
                    
                    card += "</div>"
                    product_html_list.append(card)
                
                final_html_output = "".join(product_html_list)

                # 2. Generate Text Context for LLM
                product_text_summary = "\n".join([f"- {p['title']} ({p['price']}d): {p.get('description', '')[:150]}..." for p in products])
                context_data = f"Hệ thống đã tìm thấy các sản phẩm sau từ Mecobooks:\n{product_text_summary}"
                
                # 3. Get a short intro from LLM
                intro_prompt = f"""
                {self.system_prompt}
                Người dùng muốn tìm: "{query_to_use}"
                Hệ thống tìm thấy các sách sau (kèm mô tả sơ lược):
                {product_text_summary}
                
                Hãy viết lời tư vấn ngắn gọn (khoảng 1-2 câu), dựa vào mô tả sách để khuyên người dùng nên chọn cuốn nào nếu phù hợp.
                Nếu không có thông tin mô tả cụ thể, chỉ cần mời khách xem danh sách bên dưới.
                """
                llm_intro = self.llm.generate_response(intro_prompt)
                
                return f"{llm_intro}<br/><br/>{final_html_output}"
            else:
                return "Xin lỗi, mình không tìm thấy sản phẩm nào phù hợp bên Mecobooks ạ."

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
