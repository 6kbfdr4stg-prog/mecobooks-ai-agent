import os
import logging
from datetime import datetime
from haravan_client import HaravanClient
from woocommerce_client import WooCommerceClient
from database import get_db_connection

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class InventoryOpsAgent:
    def __init__(self):
        self.logger = logging.getLogger("inventory_ops")
        self.haravan = HaravanClient()
        self.woo = WooCommerceClient()
        self.reports_dir = "/app/reports" if os.path.exists("/app") else "reports"
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # Thresholds
        self.LOW_STOCK_THRESHOLD = 5
        self.HOT_ITEM_SALES_THRESHOLD = 1 

    def run_sync(self):
        """
        Main sync logic:
        1. Fetch Haravan (Master)
        2. Fetch WooCommerce
        3. Compare and Update
        """
        self.logger.info("📦 Starting Inventory Sync...")
        
        # 1. Fetch Haravan Data
        h_products = self.haravan.get_products(limit=100)
        h_inventory = {}
        for p in h_products:
            # Haravan might have SKU in variants[0]
            # If not, let's look at the mapping logic
            sku = p.get('sku')
            
            # Fallback: Constructed SKU if real SKU is missing
            # Pattern observed in WooCommerce: HRV-{product_id}-{variant_id}
            if not sku:
                sku = f"HRV-{p['id']}-{p.get('variant_id', '')}"
                
            if sku:
                h_inventory[sku] = {
                    "name": p['title'],
                    "qty": p.get('inventory_quantity', 0)
                }
        
        # 2. Fetch WooCommerce Data
        w_inventory_list = self.woo.get_all_inventory(limit=100)
        w_inventory = {item['sku']: item for item in w_inventory_list if item.get('sku')}
        
        results = {
            "synced": [],
            "mismatch_fixed": [],
            "low_stock": [],
            "hot_items": [],
            "errors": []
        }
        
        # 3. Compare and Sync
        for sku, h_data in h_inventory.items():
            h_qty = h_data['qty']
            w_data = w_inventory.get(sku)
            
            if not w_data:
                # SKU exists in Haravan but not in Woo or no SKU mapping
                continue
                
            w_qty = w_data.get('stock_quantity', 0)
            w_sales = w_data.get('total_sales', 0)
            
            # Sync Check
            if h_qty != w_qty:
                self.logger.info(f"🔄 Mismatch for {sku}: H({h_qty}) != W({w_qty}). Updating...")
                success = self.woo.update_stock_by_sku(sku, h_qty)
                if success:
                    results["mismatch_fixed"].append({
                        "sku": sku, 
                        "name": h_data['name'], 
                        "old_qty": w_qty, 
                        "new_qty": h_qty
                    })
                else:
                    results["errors"].append(f"Failed to update SKU {sku}")
            else:
                results["synced"].append(sku)
                
            # Alert Logic
            if h_qty <= self.LOW_STOCK_THRESHOLD:
                item_info = {"sku": sku, "name": h_data['name'], "qty": h_qty, "sales": w_sales}
                results["low_stock"].append(item_info)
                
                if w_sales >= self.HOT_ITEM_SALES_THRESHOLD:
                    results["hot_items"].append(item_info)
                    
        return results

    def generate_report(self, results):
        """Generates a markdown report and saves to DB."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report = f"# 📦 Báo cáo Trí tuệ Kho hàng (Inventory Ops)\n\n"
        report += f"**Thời gian thực hiện**: `{timestamp}`\n\n"
        
        # 1. Summary
        report += "### 📊 Tổng quan\n"
        report += f"- Sản phẩm đã khớp: **{len(results['synced'])}**\n"
        report += f"- Sản phẩm đã đồng bộ lại: **{len(results['mismatch_fixed'])}**\n"
        report += f"- Sản phẩm sắp hết hàng: **{len(results['low_stock'])}**\n"
        report += f"- **🔥 Hàng Hot cần nhập gấp**: **{len(results['hot_items'])}**\n\n"
        
        # 2. Hot Items
        if results['hot_items']:
            report += "### 🔥 CẢNH BÁO: Hàng Hot sắp hết\n"
            report += "| SKU | Tên sản phẩm | Tồn kho | Doanh số (Woo) |\n"
            report += "| :--- | :--- | :--- | :--- |\n"
            for item in results['hot_items']:
                report += f"| {item['sku']} | {item['name']} | **{item['qty']}** | {item['sales']} |\n"
            report += "\n"
            
        # 3. Sync Details
        if results['mismatch_fixed']:
            report += "### 🔄 Chi tiết Đồng bộ\n"
            report += "| SKU | Tên sản phẩm | Cũ | Mới (Haravan) |\n"
            report += "| :--- | :--- | :--- | :--- |\n"
            for item in results['mismatch_fixed']:
                report += f"| {item['sku']} | {item['name']} | {item['old_qty']} | **{item['new_qty']}** |\n"
            report += "\n"
            
        report += "---\n*Được tạo tự động bởi Inventory Ops Agent.*"
        
        # Save to File
        filename = f"inventory_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = os.path.join(self.reports_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report)
            
        # Save to Database
        try:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute(
                "INSERT INTO reports (agent_name, report_type, content, created_at) VALUES (?, ?, ?, ?)",
                ("Inventory Ops", "Inventory Sync & Alerts", report, datetime.now())
            )
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.error(f"DB Error: {e}")
            
        return filepath, report

    def run(self):
        """Main entry point."""
        results = self.run_sync()
        report_path, report_content = self.generate_report(results)
        
        # Send Telegram Alert
        try:
            from ai_agents.telegram_client import send_telegram_message
            
            # Short summary for Telegram
            tg_msg = f"📦 <b>Inventory Ops Summary</b>\n\n"
            tg_msg += f"✅ Đã khớp: {len(results['synced'])}\n"
            tg_msg += f"🔄 Đã đồng bộ: {len(results['mismatch_fixed'])}\n"
            tg_msg += f"⚠️ Sắp hết: {len(results['low_stock'])}\n"
            if results['hot_items']:
                tg_msg += f"🔥 <b>HÀNG HOT CẦN NHẬP: {len(results['hot_items'])}</b>\n"
            
            tg_msg += f"\n<a href='https://mecobooks-ai-agent.onrender.com/verify'>Xem chi tiết trên Dashboard</a>"
            send_telegram_message(tg_msg)
        except Exception as e:
            self.logger.error(f"Telegram Error: {e}")
            
        return report_path

if __name__ == "__main__":
    agent = InventoryOpsAgent()
    agent.run()
