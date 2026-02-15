import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import sys

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from woocommerce_client import WooCommerceClient
from ai_agents.content_creator import LLMService

class EmailMarketingAgent:
    def __init__(self):
        self.woo = WooCommerceClient()
        self.llm = LLMService()
        self.sender_email = os.environ.get("EMAIL_SENDER")
        self.sender_password = os.environ.get("EMAIL_PASSWORD")
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
        # Zalo OA Link (Example)
        self.zalo_link = "https://zalo.me/s/xxxxxxxx" 

    def send_email(self, to_email, subject, body_html):
        if not self.sender_email or not self.sender_password:
            print("❌ [Email Agent] Missing EMAIL_SENDER or EMAIL_PASSWORD.")
            return

        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body_html, 'html'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            text = msg.as_string()
            server.sendmail(self.sender_email, to_email, text)
            server.quit()
            print(f"✅ [Email Agent] Sent to {to_email}")
        except Exception as e:
            print(f"❌ [Email Agent] Failed to send to {to_email}: {e}")

    def generate_email_content(self, customer_name, campaign_type, products_bought=[]):
        """
        Generate personalized email content using LLM.
        """
        product_list = ", ".join([p.get('name', 'sách') for p in products_bought])
        
        if campaign_type == "thank_you":
            prompt = f"""
            Bạn là CSKH của Tiệm Sách Anh Tuấn (MecoBooks).
            Hãy viết một email Cảm ơn gửi cho khách hàng tên "{customer_name}" vừa mua: {product_list}.
            
            Mục tiêu:
            - Cảm ơn chân thành.
            - Hướng dẫn bảo quản sách hoặc chúc đọc sách vui vẻ.
            - Mời tham gia Zalo để nhận ưu đãi (Link: {self.zalo_link}).
            - Tone giọng: Thân thiện, ấm áp, sâu sắc (như một người bạn yêu sách).
            - Định dạng: HTML cơ bản (dùng thẻ <p>, <b>, <br>).
            """
            subject = f"Cảm ơn bạn {customer_name} đã ghé Tiệm Sách Anh Tuấn ❤️"
            
        elif campaign_type == "re_engagement":
            prompt = f"""
            Bạn là CSKH của Tiệm Sách Anh Tuấn.
            Khách hàng "{customer_name}" đã 30 ngày chưa quay lại. Lần trước họ mua: {product_list}.
            
            Mục tiêu:
            - "Hỏi thăm" nhẹ nhàng (Miss you).
            - Gợi ý họ quay lại xem sách mới.
            - Tặng mã giảm giá: WELCOMEBACK (Giảm 10%).
            - Tone giọng: Nhớ nhung, tinh tế, không quá sale.
            - Định dạng: HTML cơ bản.
            """
            subject = f"{customer_name} ơi, Tiệm sách nhớ bạn! 📚"
        else:
            return "",""

        body = self.llm.generate_response(prompt)
        # Ensure HTML wrapper
        if "<html>" not in body:
            body = f"<html><body>{body}</body></html>"
            
        return subject, body

    def run_daily_campaign(self):
        print("📧 [Email Agent] Starting daily campaign...")
        
        # 1. Campaign: Thank You (Sold yesterday)
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%dT00:00:00')
        today = datetime.now().strftime('%Y-%m-%dT00:00:00')
        
        # Fetch orders created after yesterday 00:00 and before today 00:00 (Roughly yesterday)
        # Woo API 'after' is exclusive? 'before' inclusive? best to just check date string logic or rely on params.
        recent_orders = self.woo.get_orders(after=yesterday, before=today)
        
        print(f"   checking orders from {yesterday} to {today}...")
        
        if recent_orders:
            for order in recent_orders:
                customer_email = order.get('billing', {}).get('email')
                first_name = order.get('billing', {}).get('first_name', 'Bạn')
                items = order.get('line_items', [])
                
                if customer_email:
                    print(f"   -> Sending Thank You to {customer_email}")
                    subject, body = self.generate_email_content(first_name, "thank_you", items)
                    self.send_email(customer_email, subject, body)
                    
        # 2. Campaign: Re-engagement (Sold 30 days ago)
        # (Simplified: Fetch orders from 30-31 days ago range)
        days_ago_30 = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%dT00:00:00')
        days_ago_29 = (datetime.now() - timedelta(days=29)).strftime('%Y-%m-%dT00:00:00')
        
        lapsed_orders = self.woo.get_orders(after=days_ago_30, before=days_ago_29)
        
        if lapsed_orders:
             for order in lapsed_orders:
                customer_email = order.get('billing', {}).get('email')
                first_name = order.get('billing', {}).get('first_name', 'Bạn')
                items = order.get('line_items', [])
                
                if customer_email:
                    print(f"   -> Sending Miss You to {customer_email}")
                    subject, body = self.generate_email_content(first_name, "re_engagement", items)
                    self.send_email(customer_email, subject, body)

if __name__ == "__main__":
    agent = EmailMarketingAgent()
    # For testing, you might want to mock send_email or test with real creds
    # agent.run_daily_campaign()
    print("Email Agent initialized. Run run_daily_campaign() to start.")
