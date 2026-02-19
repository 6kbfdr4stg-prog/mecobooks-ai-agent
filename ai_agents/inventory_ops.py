import os
import logging
from datetime import datetime
from haravan_client import HaravanClient
from database import get_db_connection

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class InventoryOpsAgent:
    def __init__(self):
        self.logger = logging.getLogger("inventory_ops")
        self.haravan = HaravanClient()
        self.reports_dir = "/app/reports" if os.path.exists("/app") else "reports"
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # Thresholds
        self.LOW_STOCK_THRESHOLD = 5
        self.HOT_ITEM_SALES_THRESHOLD = 3 # Increased threshold for Haravan sales

    def run_monitor(self):
        """
        Main monitor logic:
        1. Fetch Haravan Inventory
        2. Fetch Haravan Sales (Last 30 days)
        3. Identify Low Stock and Hot Items
        """
        print("📦 Starting Haravan Inventory Monitor Agent...")
        
        # 1. Fetch Haravan Inventory
        h_variants = self.haravan.get_products(limit=250)
        h_inventory = {}
        for v in h_variants:
            raw_sku = v.get('sku')
            if raw_sku:
                # Normalize SKU
                sku = str(raw_sku).strip().upper()
                h_inventory[sku] = {
                    "name": v['title'],
                    "qty": v.get('inventory_quantity', 0)
                }
        print(f"✅ Fetched {len(h_inventory)} variants from Haravan.")
        
        # 2. Fetch Haravan Sales Data
        v_sales = self.haravan.get_variant_sales(days=30)
        print(f"✅ Analyzed sales for {len(v_sales)} variants on Haravan.")
        
        results = {
            "monitored": len(h_inventory),
            "low_stock": [],
            "hot_items": [],
            "errors": []
        }
        
        # 3. Analyze
        for sku, h_data in h_inventory.items():
            h_qty = h_data['qty']
            h_sales = v_sales.get(sku, 0)
            
            # Alert Logic
            if h_qty <= self.LOW_STOCK_THRESHOLD:
                item_info = {"sku": sku, "name": h_data['name'], "qty": h_qty, "sales": h_sales}
                results["low_stock"].append(item_info)
                
                if h_sales >= self.HOT_ITEM_SALES_THRESHOLD:
                    results["hot_items"].append(item_info)
        
        print(f"📊 Monitor Completed. Low Stock: {len(results['low_stock'])}, Hot Items: {len(results['hot_items'])}")
        return results

    def generate_report(self, results):
        """Generates a markdown report and saves to DB."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report = f"# 📦 Báo cáo Giám sát Kho hàng (Haravan Monitor)\n\n"
        report += f"**Thời gian thực hiện**: `{timestamp}`\n\n"
        
        # 1. Summary
        report += "### 📊 Tổng quan\n"
        report += f"- Tổng số biến thể theo dõi: **{results['monitored']}**\n"
        report += f"- Sản phẩm sắp hết hàng: **{len(results['low_stock'])}**\n"
        report += f"- **🔥 Hàng Hot cần nhập gấp**: **{len(results['hot_items'])}**\n\n"
        
        # 2. Hot Items
        if results['hot_items']:
            report += "### 🔥 CẢNH BÁO: Hàng Hot sắp hết\n"
            report += "| SKU | Tên sản phẩm | Tồn kho | Doanh số (30 ngày) |\n"
            report += "| :--- | :--- | :--- | :--- |\n"
            for item in results['hot_items']:
                report += f"| {item['sku']} | {item['name']} | **{item['qty']}** | {item['sales']} |\n"
            report += "\n"
            
        # 3. Low Stock Details
        if results['low_stock'] and not results['hot_items']:
             report += "### ⚠️ Danh sách hàng tồn thấp\n"
             report += "| SKU | Tên sản phẩm | Tồn kho |\n"
             report += "| :--- | :--- | :--- |\n"
             for item in results['low_stock'][:10]: # Limit to top 10
                 report += f"| {item['sku']} | {item['name']} | {item['qty']} |\n"
             if len(results['low_stock']) > 10:
                 report += f"\n*...và {len(results['low_stock']) - 10} sản phẩm khác.*"
             report += "\n"
            
        report += "---\n*Được tạo tự động bởi Haravan Inventory Monitor Agent.*"
        
        # Save to Database
        try:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute(
                "INSERT INTO reports (agent_name, report_type, content, created_at) VALUES (?, ?, ?, ?)",
                ("Inventory Ops", "Haravan Inventory Monitor", report, datetime.now())
            )
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.error(f"DB Error: {e}")
            
        return report

    def run(self):
        """Main entry point."""
        results = self.run_monitor()
        report_content = self.generate_report(results)
        
        # Send Telegram Alert
        try:
            from ai_agents.telegram_client import send_telegram_message
            
            tg_msg = f"📦 <b>Haravan Inventory Monitor</b>\n\n"
            tg_msg += f"✅ Tổng theo dõi: {results['monitored']}\n"
            tg_msg += f"⚠️ Sắp hết: {len(results['low_stock'])}\n"
            if results['hot_items']:
                tg_msg += f"🔥 <b>HÀNG HOT CẦN NHẬP: {len(results['hot_items'])}</b>\n"
            
            tg_msg += f"\n<a href='https://mecobooks-ai-agent.onrender.com/verify'>Xem chi tiết trên Dashboard</a>"
            send_telegram_message(tg_msg)
        except Exception as e:
            self.logger.error(f"Telegram Error: {e}")
            
        return report_content

if __name__ == "__main__":
    agent = InventoryOpsAgent()
    agent.run()
