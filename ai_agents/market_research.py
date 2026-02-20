
import os
import sys
from datetime import datetime

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chatbot import Chatbot
from utils.logger import setup_logger
from config import get_now_hanoi

class MarketResearchAgent:
    def __init__(self):
        self.logger = setup_logger("market_research_agent")
        self.bot = Chatbot()
        # Email Notifier
        try:
            from utils.email_notifier import EmailNotifier
            self.notifier = EmailNotifier()
        except ImportError:
            self.notifier = None
        # Use absolute path to ensure consistency between local/docker/manual execution
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.report_dir = os.path.join(self.project_root, "reports_v2")
        os.makedirs(self.report_dir, exist_ok=True)
        
        # Haravan Client for catalog audit
        from haravan_client import HaravanClient
        self.hrv = HaravanClient()

    def run(self):
        """
        Main execution of the Market Research Agent.
        """
        print("🔍 [Market Research Agent] Starting research for 2025 book trends...")
        self.logger.info("Starting Market Research")

        try:
            # 1. Fetch Haravan Catalog for Matching
            print("📦 [Market Research] Fetching Haravan catalog for auditing...")
            hrv_products = self.hrv.get_all_products()
            hrv_titles_set = {p['product_name'].lower().strip() for p in hrv_products}
            
            # 2. Researching Trends
            now_hrv = get_now_hanoi()
            today = now_hrv.strftime("%Y-%m-%d")
            
            prompt = f"""
            Hôm nay là ngày {today}. Bạn là một chuyên gia nghiên cứu thị trường sách tại Việt Nam. 
            
            NHIỆM VỤ:
            Tìm kiếm và liệt kê TỐI THIỂU 50 cuốn sách ĐANG HOT NHẤT (Bán chạy, được nhắc tới nhiều) tại Việt Nam tháng 2/2025.
            
            Bảng kết quả cần 4 cột:
            | Thể loại | Tên sách | Nguồn nhập đề xuất | Giá tham khảo |
            
            Yêu cầu: Viết bằng tiếng Việt, định dạng Markdown chuyên nghiệp.
            """
            
            report_content = self.bot.llm.generate_response(prompt)
            
            # 3. Audit matching in Python (Robust)
            import re
            lines = report_content.split('\n')
            new_lines = []
            for line in lines:
                if '|' in line and not any(h in line for h in ['Thể loại', '---']):
                    cols = [c.strip() for c in line.split('|')]
                    if len(cols) >= 3:
                        book_name = cols[2].lower().strip()
                        status = "🆕 Cần nhập"
                        # Simple substring match for robustness
                        for hrv_t in hrv_titles_set:
                            if book_name in hrv_t or hrv_t in book_name:
                                status = "✅ Đã có"
                                break
                        line = line.rstrip('| ') + f" | {status} |"
                elif 'Thể loại' in line:
                    line = line.rstrip('| ') + " | Trạng thái |"
                elif '---' in line:
                    line = line.rstrip('| ') + " | :---: |"
                new_lines.append(line)
            
            report_content = '\n'.join(new_lines)
            
            # 2. Save Report
            report_path = os.path.join(self.report_dir, "market_research_latest.md")
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(f"# BÁO CÁO NGHIÊN CỨU THỊ TRƯỜNG - {today}\n\n")
                f.write(report_content)
                f.write("\n\n---\n*Báo cáo được tạo tự động bởi AI Market Research Agent.*")

            print(f"✅ [Market Research Agent] Report generated at {report_path}")
            self.logger.info("Market Research Report generated", extra={"metadata": {"path": report_path}})

            # 3. Export to Sheets (via n8n)
            self.parse_and_export(report_content)
            
            return {
                "report_path": report_path,
                "content": report_content
            }

        except Exception as e:
            print(f"❌ [Market Research Agent] Error: {e}")
            self.logger.error("Market Research Error", exc_info=True)
            return {"error": str(e)}

    def parse_and_export(self, markdown_text):
        """
        Parses the markdown table and sends data to n8n for Google Sheets export.
        """
        import re
        import requests

        # Flexible regex to find ANY table row with 4-6 columns
        table_pattern = r"\| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?)\|"
        matches = re.findall(table_pattern, markdown_text)
        
        print(f"DEBUG: Found {len(matches)} matches in the markdown table.")

        if not matches:
            print("⚠️ [Market Research Agent] No data table found to export.")
            return

        # Filter out header and separator lines
        data_rows = []
        for row in matches:
            # Clean up the row
            row = [c.strip() for c in row]
            
            # Identify headers
            if row[0] in ["Thể loại", "STT", "No.", "No", "---", ":---", ":---:", "---:"]:
                continue
            
            # Mapping for 5-column: Category | Title | Sub-Category | Supplier | Price
            # We map: 
            # category = row[0]
            # book_name = row[1]
            # supplier = row[3]
            # price = row[4]
            
            if len(row) >= 5:
                category = row[0]
                book_name = row[1]
                supplier = row[3]
                price_benchmark = row[4]
            else:
                # Fallback mapping
                category = row[0]
                book_name = row[1]
                supplier = row[2]
                price_benchmark = row[3]

            if not book_name or book_name == "---":
                continue
                
            data_rows.append({
                "date": get_now_hanoi().strftime("%Y-%m-%d"),
                "category": category,
                "book_name": book_name,
                "supplier": supplier,
                "price_benchmark": price_benchmark
            })

        if not data_rows:
            print("⚠️ [Market Research Agent] No valid rows found in table.")
            return

        # Send to Webhook (Google Apps Script or n8n)
        webhook_url = os.environ.get("GOOGLE_SHEETS_WEBHOOK_URL") or os.environ.get("N8N_RESEARCH_WEBHOOK_URL")
        if not webhook_url:
            print("⚠️ [Market Research Agent] Missing GOOGLE_SHEETS_WEBHOOK_URL or N8N_RESEARCH_WEBHOOK_URL. Export skipped.")
        else:
            print(f"🚀 [Market Research Agent] Exporting {len(data_rows)} rows to Google Sheets...")
            try:
                response = requests.post(webhook_url, json={"data": data_rows})
                if response.status_code == 200:
                    print("✅ [Market Research Agent] Data sent to Google Sheets successfully!")
                else:
                    print(f"❌ [Market Research Agent] Export failed: {response.text}")
            except Exception as e:
                print(f"❌ [Market Research Agent] Error exporting data: {e}")

        # 4. Generate & Send Blog Post (WordPress direct API)
        self.publish_blog_post(data_rows, markdown_text)

    def publish_blog_post(self, data_rows, markdown_text=""):
        """Generates an HTML blog post and publishes directly to WordPress API."""
        import requests
        import base64
        import datetime
        
        # Sắp xếp lại dữ liệu: gom nhóm theo Category
        books_by_category = {}
        for row in data_rows:
            category = row.get('category', 'Sách Bán Chạy & Xu Hướng')
            if category not in books_by_category:
                books_by_category[category] = []
            books_by_category[category].append(row)
            
        current_date_str = get_now_hanoi().strftime("%d/%m/%Y")
        title = f"Top 50+ Sách Hot Trend - Cập nhật ngày {current_date_str}"
        
        # HTML Header & Intro
        html_content = f"""
        <p>Chào bạn,</p>
        <p>Dưới đây là danh sách tổng hợp hơn 50 cuốn sách đang được quan tâm và tìm kiếm nhiều nhất trên thị trường vào ngày {current_date_str}.</p>
        <p>Danh sách này được AI tổng hợp dựa trên dữ liệu từ Google Trends, Tiki, Fahasa, Shopee và các trang đánh giá sách uy tín.</p>
        <hr />
        """
        
        # Generate Body Content
        for category, books in books_by_category.items():
            html_content += f"<h2>📚 Thể loại: {category} ({len(books)} cuốn)</h2>"
            html_content += "<ul>"
            for book in books:
                # Map keys from parse_and_export
                book_title = book.get('book_name', 'N/A')
                supplier = book.get('supplier', 'N/A')
                price = book.get('price_benchmark', 'N/A')
                
                html_content += f"<li><strong>{book_title}</strong><br/>"
                html_content += f"Gợi ý nguồn nhập: {supplier}<br/>"
                html_content += f"Giá/Chiết khấu tham khảo: {price}</li><br/>"
            html_content += "</ul>"
            
        # Call-to-action Footer
        html_content += """
        <hr />
        <p><em>Lưu ý: Giá sách có thể thay đổi tùy thời điểm và nhà cung cấp.</em></p>
        <p>Bạn quan tâm đến cuốn nào nhất? Hãy để lại bình luận hoặc liên hệ MecoBooks để được tư vấn nguồn hàng nhé!</p>
        """
        
        # WordPress API Posting Logic
        wp_url = "https://mecobooks.com/wp-json/wp/v2/posts"
        username = "admin"
        # Using the hardcoded App Password for stability as per troubleshooting
        app_password = "dQcO 8nD1 qa5U ui7K JyIL iBTa" 
        
        credentials = f"{username}:{app_password}"
        token = base64.b64encode(credentials.encode()).decode('utf-8')
        
        headers = {
            'Authorization': f'Basic {token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "title": title,
            "content": html_content,
            "status": "publish" # Set to 'draft' if you want to review first
        }
        
        print("🚀 Publishing blog post directly to WordPress API...")
        try:
            response = requests.post(wp_url, headers=headers, json=payload, timeout=30)
            if response.status_code in [200, 201]:
                print(f"✅ Blog post published successfully! ID: {response.json().get('id')}")
                print(f"🔗 Link: {response.json().get('link')}")
            else:
                print(f"❌ Failed to publish blog post. Status Code: {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"❌ Exception sending request to WordPress: {e}")

        # Email Notification
        if self.notifier:
            subject = "📈 [Research] Báo cáo Xu hướng Sách mới"
            body = f"""
            <html><body>
            <h3>Nghiên cứu thị trường hoàn tất!</h3>
            <p>Đã tìm thấy {len(data_rows)} cuốn sách hot.</p>
            <p>Dữ liệu đã được gửi về Google Sheets và đăng lên Blog Mecobooks.</p>
            <pre>{markdown_text[:500]}...</pre>
            </body></html>
            """
            self.notifier.send_report(subject, body)


if __name__ == "__main__":
    agent = MarketResearchAgent()
    agent.run()
