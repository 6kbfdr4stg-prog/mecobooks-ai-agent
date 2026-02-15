
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

    def handle_customer_query(self, query):
        """
        Enhanced query handler.
        Interprets if the user is asking about a specific book availability
        and fetches real-time data before answering.
        """
        print(f"🤖 [Sales Agent] Processing: '{query}'")
        
        # Simple keyword extraction (could be LLM based for better intent)
        # If query contains "có ... không" or "sách ... còn không", search woo
        
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
                response = self.bot.chat(f"{product_context}\n\nKhách hỏi: {query}", system_instruction)
                return response
            else:
                return self.bot.chat(query, "Khách hỏi về sách nhưng không tìm thấy trong kho. Hãy xin lỗi và gợi ý họ nhắn tin Zalo để admin kiểm tra kỹ hơn.")
        
        # Default chat
        return self.bot.chat(query)

    def process_message(self, message, platform="web", image_url=None, image_data=None):
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
        
        return self.handle_customer_query(message)

if __name__ == "__main__":
    agent = SalesSupportAgent()
    print(agent.handle_customer_query("Bạn có sách Nhà Giả Kim không?"))
