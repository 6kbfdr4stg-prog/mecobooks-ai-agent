import os
import sys
import logging
from datetime import datetime, timedelta

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from haravan_client import HaravanClient
from config import get_now_hanoi
from ai_agents.telegram_client import send_telegram_message

logger = logging.getLogger("bi_analyst")

class BIAnalystAgent:
    def __init__(self):
        self.hrv = HaravanClient()

    def run_daily_summary(self):
        """
        Generates and sends a daily business summary for yesterday.
        """
        logger.info("📊 BI Analyst: Generating daily summary...")
        
        now = get_now_hanoi()
        yesterday = now - timedelta(days=1)
        yesterday_str = yesterday.strftime("%Y-%m-%d")

        # 1. Fetch Sales
        sales_data = self.hrv.get_daily_revenue(period="7days")
        yesterday_rev = sales_data.get(yesterday_str, 0)
        
        # 2. Fetch Orders Count (Estimate or detail fetch)
        # For simplicity, we'll use the daily summary from Haravan if possible
        # or just report revenue trend
        avg_rev = sum(sales_data.values()) / max(1, len(sales_data))
        performance = "Ổn định"
        if yesterday_rev > avg_rev * 1.2: performance = "🔥 Bùng nổ"
        elif yesterday_rev < avg_rev * 0.8: performance = "📉 Thấp hơn trung bình"

        # 3. Inventory Check
        from ai_agents.inventory_analyst import InventoryAnalystAgent
        inv_agent = InventoryAnalystAgent()
        inv_report = inv_agent.analyze_stock()
        
        # 4. Craft Message
        msg = f"<b>📊 BÁO CÁO ĐIỀU HÀNH MECBOOKS ({yesterday_str})</b>\n\n"
        msg += f"💰 <b>Doanh thu:</b> {yesterday_rev:,.0f} ₫\n"
        msg += f"📈 <b>Trạng thái:</b> {performance}\n"
        msg += f"📦 <b>Tồn kho:</b> {len(inv_report.get('group_a', []))} sp Hot | {len(inv_report.get('group_c', []))} sp Tồn\n\n"
        
        if inv_report.get('fast_movers'):
            msg += "⚠️ <b>CẢNH BÁO HẾT HÀNG:</b>\n"
            for p in inv_report['fast_movers'][:3]:
                msg += f"- {p['title']} (Chỉ còn {p.get('inventory_quantity', 0)})\n"
            msg += "\n"

        msg += "🚀 <i>Hệ thống AI đã sẵn sàng cho ngày mới!</i>"

        # 5. Send (Strict)
        try:
            send_telegram_message(msg)
            return {"status": "success", "message": f"Daily summary for {yesterday_str} sent to Telegram"}
        except Exception as e:
            logger.error(f"BI Agent failed at notification step: {e}")
            raise  # Propagate to Overseer/Server to mark as Failure

if __name__ == "__main__":
    agent = BIAnalystAgent()
    print(agent.run_daily_summary())
