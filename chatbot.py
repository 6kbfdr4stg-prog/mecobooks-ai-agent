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
                product_info = []
                for p in products:
                    info = f"- {p['title']}: {p['price']} VND"
                    if p.get('variant_id'):
                        # Generate Haravan Checkout Link
                        checkout_link = f"{self.haravan.shop_url}/cart/{p['variant_id']}:1"
                        info += f"\n  👉 Mua ngay: {checkout_link}"
                    product_info.append(info)
                
                product_list = "\n".join(product_info)
                context_data = f"Tìm thấy các sản phẩm sau cho từ khóa '{query_to_use}':\n{product_list}\nChi tiết: {json.dumps(products, ensure_ascii=False)}"
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
