import os
import sys
import json
from collections import Counter

# Add parent dir to path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_service import LLMService
from haravan_client import HaravanClient
from ai_agents.telegram_client import send_telegram_message

class StrategicAnalystAgent:
    def __init__(self):
        self.hrv = HaravanClient()
        self.llm = LLMService()
        self.log_file = "logs/app.jsonl"

    def analyze_recent_demand(self, limit=100):
        """
        Parses logs to find what customers are actually asking for.
        """
        if not os.path.exists(self.log_file):
            return "No logs found."
        
        queries = []
        with open(self.log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            # Read last 'limit' lines
            for line in lines[-limit:]:
                try:
                    data = json.loads(line)
                    meta = data.get("metadata", {})
                    if meta.get("event") == "USER_QUERY":
                        queries.append(meta.get("query", ""))
                except:
                    continue
        
        if not queries:
            return "No recent queries found."
            
        # Use LLM to summarize demand
        prompt = f"""
        Dưới đây là danh sách {len(queries)} yêu cầu gần nhất của khách hàng tại Tiệm Sách Anh Tuấn:
        ---
        {chr(10).join(queries)}
        ---
        Hãy phân tích và tóm tắt ngắn gọn (3-5 gạch đầu dòng):
        1. Xu hướng quan tâm chính (Khách muốn mua gì/hỏi gì nhiều nhất?).
        2. Các đầu sách hoặc chủ đề khách hỏi nhưng hệ thống có thể chưa đáp ứng tốt.
        3. Gợi ý hành động kinh doanh ngay lập tức.
        Kết quả viết bằng Tiếng Việt.
        """
        return self.llm.generate_response(prompt)

    def generate_growth_strategy(self, inventory_report):
        """
        Combines inventory data with log demand to give a 1-week strategy.
        """
        demand_summary = self.analyze_recent_demand()
        
        prompt = f"""
        Bạn là Giám đốc Chiến lược (Chief Strategy Officer) của Tiệm Sách Anh Tuấn.
        
        DỮ LIỆU ĐẦU VÀO:
        1. Tóm tắt nhu cầu khách (từ nhật ký chat):
        {demand_summary}
        
        2. Tóm tắt tình trạng kho hàng:
        {inventory_report}
        
        NHIỆM VỤ:
        Hãy đưa ra một bản 'Chiến lược tăng trưởng tuần tới' cực kỳ ngắn gọn, sắc bén:
        - THÁCH THỨC: Điểm nghẽn lớn nhất hiện tại là gì?
        - CƠ HỘI: Đâu là 'mỏ vàng' chưa khai thác?
        - HÀNH ĐỘNG: 3 việc cụ thể admin phải làm ngay (Ví dụ: Nhập thêm X, giảm giá Y, đẩy content Z).
        
        Viết bằng Tiếng Việt, phong cách chuyên nghiệp, quyết đoán.
        """
        return self.llm.generate_response(prompt)

    def analyze_revenue_depth(self):
        """
        Provides a deep dive into revenue trends and product performance.
        """
        print("🤖 [Strategic Agent] Performing Revenue Deep Dive...")
        
        # 1. Get Core Stats
        stats = self.hrv.get_sales_report(period="month")
        
        # 2. Get Daily Trends
        daily_trends = self.hrv.get_daily_revenue(period="month")
        
        # 3. Get Top Revenue Items
        top_items = self.hrv.get_product_revenue_ranking(days=30)
        
        # 4. Format for LLM
        trends_str = "\n".join([f"- {d}: {v:,.0f} đ" for d, v in sorted(daily_trends.items())])
        top_str = "\n".join([f"- {name}: {rev:,.0f} đ" for name, rev in top_items[:10]])
        
        prompt = f"""
        Bạn là Chuyên gia Phân tích Tài chính của Tiệm Sách Anh Tuấn.
        Dưới đây là dữ liệu doanh thu chi tiết trong tháng này (Hỗ trợ bởi Haravan):
        
        TỔNG QUAN:
        - Tổng doanh thu thuần: {stats['total_sales']:,.0f} đ
        - Tổng số đơn hàng thành công: {stats['total_orders']}
        - Số lượng khách hàng: {stats['total_customers']}
        
        XU HƯỚNG THEO NGÀY:
        {trends_str}
        
        TOP 10 SẢN PHẨM MANG LẠI DÒNG TIỀN LỚN NHẤT:
        {top_str}
        
        NHIỆM VỤ:
        Hãy viết một báo cáo phân tích sâu (Deep Dive) bao gồm:
        1. Nhận xét về xu hướng tăng trưởng theo ngày (Ngày nào đột biến? Tại sao có thể như vậy?).
        2. Phân tích về danh mục sản phẩm chủ lực (Các sản phẩm mang lại nhiều tiền nhất có chung đặc điểm gì?).
        3. Dự báo doanh thu cuối tháng dựa trên tốc độ hiện tại.
        4. Đề xuất hành động cụ thể để tối ưu hóa doanh thu (Ví dụ: Đẩy mạnh marketing sản phẩm X, hoặc tạo combo cho ngày Y).
        
        Viết bằng Tiếng Việt, phong cách sắc bén, hướng tới hành động.
        """
        return self.llm.generate_response(prompt)

    def run(self):
        """Standardized run method for Strategic Analyst."""
        print("🚀 [Strategic Agent] Running complete weekly analysis...")
        
        # 1. Growth Strategy
        from ai_agents.inventory_analyst import InventoryAnalystAgent
        inv_agent = InventoryAnalystAgent()
        inv_report = inv_agent.analyze_stock()
        growth_strategy = self.generate_growth_strategy(inv_report)
        
        # 2. Revenue Deep Dive
        revenue_deep_dive = self.analyze_revenue_depth()
        
        # 3. Save as Markdown Report
        timestamp = get_now_hanoi().strftime("%Y-%m-%d %H:%M:%S")
        report = f"# 🚀 BÁO CÁO CHIẾN LƯỢC TĂNG TRƯỞNG\n\n"
        report += f"**Thời gian**: `{timestamp}`\n\n"
        report += f"## 📈 Chiến lược Tuần tới\n\n{growth_strategy}\n\n"
        report += f"## 💰 Phân tích Doanh thu chuyên sâu\n\n{revenue_deep_dive}\n\n"
        report += f"---\n*Báo cáo được tạo bởi Strategic Analyst Agent.*"
        
        # Send Telegram Notification (Phase 9)
        try:
            tg_msg = f"🚀 <b>Weekly Strategic Analysis Ready</b>\n\n"
            tg_msg += f"📊 Đã hoàn thành phân tích doanh thu và chiến lược tăng trưởng tuần tới.\n"
            tg_msg += f"\n<a href='https://mecobooks-ai-agent.onrender.com/verify'>Xem báo cáo chi tiết</a>"
            send_telegram_message(tg_msg)
        except: pass
        
        return report

if __name__ == "__main__":
    analyst = StrategicAnalystAgent()
    # Mock inventory report for testing
    mock_report = "Nhóm A (Bán chạy): Sách kinh doanh (Tồn thấp). Nhóm C (Tồn kho): Sách văn học cũ (Tồn cao)."
    print("--- STRATEGIC ANALYSIS ---")
    print(analyst.generate_growth_strategy(mock_report))
