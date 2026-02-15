
import os
import sys

# Add parent dir to path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from woocommerce_client import WooCommerceClient
from llm_service import LLMService
# from video_generator import create_video_from_product # Placeholder for future

class ContentCreatorAgent:
    def __init__(self):
        self.woo = WooCommerceClient()
        self.llm = LLMService()

    def get_trending_news(self):
        """
        Fetches trending news from Google News RSS (Vietnam).
        Returns a list of top titles.
        """
        import feedparser
        rss_url = "https://news.google.com/rss?hl=vi&gl=VN&ceid=VN:vi"
        try:
            feed = feedparser.parse(rss_url)
            if feed.entries:
                return [entry.title for entry in feed.entries[:5]] # Get top 5
        except Exception as e:
            print(f"⚠️ News Fetch Error: {e}")
        return []

    def generate_daily_content(self, platform="facebook"):
        """
        Main function to generate daily content.
        1. Checks for Trending News (Newsjacking).
        2. Picks a product relevant to trend OR random.
        3. Generates a caption using LLM.
        """
        print(f"🤖 [Content Agent] Starting daily content generation for {platform}...")
        
        # 1. Get Trends
        trends = self.get_trending_news()
        trend_context = ""
        selected_trend = ""
        
        if trends:
            import random
            selected_trend = random.choice(trends)
            print(f"🔥 [Trend Detected] {selected_trend}")
            trend_context = f"\nSự kiện/Tin tức đang hot: '{selected_trend}'"

        # 2. Select Product
        # Ideal: Search woo based on trend. For now, random or specific keyword based on trend (advanced)
        # Simplified: Pick random product but link story to proper trend
        products = self.woo.search_products("sách", limit=20)
        
        if not products:
            return "⚠️ [Content Agent] No products found to promote."

        import random
        product = random.choice(products)
        print(f"   Selected Product: {product['title']}")
 
        # 3. Generate Caption
        prompt = f"""
        Bạn là một chuyên gia sáng tạo nội dung cho Tiệm Sách Anh Tuấn (mecobooks.com).
        {trend_context}
        
        Hãy viết một bài đăng {platform} hấp dẫn để giới thiệu cuốn sách: "{product['title']}".
        
        Thông tin sách:
        - Giá: {product['price']} VNĐ
        - Tình trạng: {product['inventory_text']}
        - Tình trạng: {product['inventory_text']}
        - Link mua hàng: {product['url']} (LƯU Ý: KHÔNG chèn link này vào bài viết, chỉ viết nội dung kêu gọi. Link sẽ được để dưới comment).
        
        Yêu cầu:
        - Tone giọng: Nhẹ nhàng, sâu sắc, tinh tế, kể chuyện (storytelling).
        - Tuyệt đối KHÔNG giật tít, KHÔNG gây sốc, KHÔNG dùng ngôn ngữ chợ búa.
        - {f"QUAN TRỌNG: Hãy khéo léo dẫn dắt từ sự kiện '{selected_trend}' sang nội dung cuốn sách một cách tự nhiên (nếu thấy không liên quan thì không cần ép buộc, cứ viết tự nhiên)." if selected_trend else ""}
        - Tập trung vào giá trị tinh thần và cảm xúc mà cuốn sách mang lại.
        - Có Call To Action nhẹ nhàng (ví dụ: "Mời bạn ghé đọc...", "Link mình để dưới comment...").
        - Sử dụng icon và hashtag phù hợp (#MecoBooks #SachHay ...).
        - Độ dài: Khoảng 150-200 từ.
        - TUYỆT ĐỐI KHÔNG CHÈN URL VÀO BÀI VIẾT.
        
        ---
        PHẦN 2: KỊCH BẢN VIDEO NGẮN (REELS/TIKTOK)
        Hãy viết thêm một kịch bản ngắn (khoảng 30-40 giây đọc) để làm video giới thiệu sách này. 
        Chỉ viết lời bình (Voiceover), không cần chỉ dẫn hình ảnh.
        Bắt đầu bằng: "SCRIPT_VIDEO:"
        """
        
        full_response = self.llm.generate_response(prompt)
        
        # Split caption and script
        parts = full_response.split("SCRIPT_VIDEO:")
        caption = parts[0].strip()
        video_script = parts[1].strip() if len(parts) > 1 else f"Giới thiệu cuốn sách {product['title']}. Một tác phẩm tuyệt vời bạn không nên bỏ lỡ."

        # 4. Generate Video
        video_url = ""
        # SKIP VIDEO GENERATION ON RENDER (Due to missing ImageMagick)
        # try:
        #     from video_processor import VideoProcessor
        #     vp = VideoProcessor()
        #     video_path = vp.generate_video({
        #         "title": product['title'],
        #         "image_url": product['image'],
        #         "script": video_script,
        #         "id": f"{product['id']}_{int(time.time())}"
        #     })
        #     
        #     if video_path:
        #         # Convert local path to URL
        #         filename = os.path.basename(video_path)
        #         # Use the Render URL (or localhost if testing)
        #         video_url = f"https://mecobooks-ai-agent.onrender.com/static/videos/{filename}"
        #         print(f"🎥 [Content Agent] Video created: {video_url}")
        # except Exception as e:
        #     print(f"❌ [Content Agent] Video generation failed: {e}")

        return {
            "product": product,
            "caption": caption,
            "image_url": product['image'],
            "video_url": video_url,
            "video_script": video_script
        }

    def send_to_webhook(self, content):
        """
        Send generated content to a Webhook (Make/n8n) for distribution.
        """
        import requests
        webhook_url = os.environ.get("MAKE_WEBHOOK_URL")

        if not webhook_url:
            print("⚠️ [Content Agent] Missing MAKE_WEBHOOK_URL. Content generated but not sent.")
            return

        print(f"🚀 [Content Agent] Sending content to Webhook...")
        
        payload = {
            "title": content['product']['title'],
            "price": content['product']['price'],
            "image_url": content['image_url'],
            "caption": content['caption'],
            "link": content['product']['url'],
            "video_url": content.get('video_url', ''),
            "source": "ai_agent"
        }

        try:
            response = requests.post(webhook_url, json=payload)
            if response.status_code == 200:
                print(f"✅ [Content Agent] Webhook trigger successful!")
            else:
                print(f"❌ [Content Agent] Webhook trigger failed: {response.text}")
        except Exception as e:
            print(f"❌ [Content Agent] Error sending to Webhook: {e}")


if __name__ == "__main__":
    agent = ContentCreatorAgent()
    content = agent.generate_daily_content()
    print("\n--- GENERATED CONTENT ---\n")
    print(content)
    
    # Test Webhook
    if content and isinstance(content, dict):
        agent.send_to_webhook(content)
