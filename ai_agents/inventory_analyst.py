
import os
import sys

# Add parent dir to path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from haravan_client import HaravanClient

class InventoryAnalystAgent:
    def __init__(self):
        self.hrv = HaravanClient()
        # Email Notifier
        try:
            from utils.email_notifier import EmailNotifier
            self.notifier = EmailNotifier()
        except ImportError:
            self.notifier = None
            print("⚠️ [Inventory] EmailNotifier not found. Skipping email reports.")

    def analyze_stock(self, days=30):
        """
        Analyzes stock using ABC Analysis (Pareto Principle):
        - Group A (Best Sellers): Top 20% of products by sales.
        - Group C (Dead Stock): 0 Sales & In Stock.
        - Group B (Standard): The rest.
        """
        print(f"🤖 [Inventory Agent] Starting ABC Inventory Analysis for last {days} days...")
        
        # 1. Fetch All Variants
        variants = self.hrv.get_all_products()
        if not variants:
            return {"error": "No products found on Haravan"}

        # 2. Fetch Sales Data
        sku_sales = self.hrv.get_variant_sales(days=days)
        
        # 3. Merge & Process
        processed_items = []
        for v in variants:
            sku = v.get('sku', '').upper()
            sales_qty = sku_sales.get(sku, 0)
            
            v['current_sales'] = sales_qty # Match new logic
            processed_items.append(v)
                
        # 4. Sort by Sales
        sorted_products = sorted(processed_items, key=lambda x: x['current_sales'], reverse=True)
        
        total_items = len(sorted_products)
        if total_items == 0:
            return {"error": "No products processed"}

        # 5. Classify
        # A: Top 20% by count (simplified ABC)
        top_20_count = max(1, int(total_items * 0.2))
        group_a = sorted_products[:top_20_count]
        
        remaining = sorted_products[top_20_count:]
        group_c = [p for p in remaining if p['current_sales'] == 0]
        group_b = [p for p in remaining if p['current_sales'] > 0]

        report = {
            "total_scanned": total_items,
            "group_a": group_a,
            "group_b": group_b,
            "group_c": group_c,
            "missing_images": [p for p in processed_items if not p.get('images')]
        }
        return report

    def identify_dead_stock(self, variants, sku_sales_90):
        """Lọc sản phẩm tồn > 5 cuốn nhưng bán = 0 trong 90 ngày."""
        dead_stock = []
        for v in variants:
            sku = v.get('sku', '').upper()
            sales = sku_sales_90.get(sku, 0)
            inventory = int(v.get('inventory_quantity', 0))
            if sales == 0 and inventory >= 5:
                dead_stock.append(v)
        return dead_stock

    def identify_fast_movers(self, variants, sku_sales_30):
        """Lọc sản phẩm bán chạy nhưng tồn thấp (< 20% lượng bán tháng)."""
        fast_movers = []
        for v in variants:
            sku = v.get('sku', '').upper()
            sales = sku_sales_30.get(sku, 0)
            inventory = int(v.get('inventory_quantity', 0))
            if sales >= 5 and inventory < (sales * 0.2):
                fast_movers.append(v)
        return fast_movers

    def generate_action_plan(self, report):
        """
        Generates a strategic action plan based on ABC analysis and deep insights.
        """
        if "error" in report:
            return "⚠️ Không tìm thấy dữ liệu sản phẩm để phân tích."

        plan = f"📊 **BÁO CÁO CHIẾN LƯỢC TỒN KHO & THỊ TRƯỜNG**\n"
        plan += f"Tổng quét: {report['total_scanned']} sản phẩm.\n\n"
        
        # 1. Fast Movers Alert
        if report.get('fast_movers'):
            plan += f"🔥 **CẢNH BÁO ĐỨT HÀNG (Sắp hết)**\n"
            plan += f"_(Bán cực chạy nhưng tồn kho quá thấp - Cần nhập ngay)_\n"
            for p in report['fast_movers'][:5]:
                plan += f"- {p['title']} (Bán: {p['current_sales']} | Tồn: {p.get('inventory_quantity', 0)})\n"
            plan += "👉 **Hành động**: Liên hệ NXB/Nhà cung cấp để đặt thêm hàng ngay hôm nay.\n\n"

        # 2. Dead Stock Strategy
        if report.get('dead_stock'):
            plan += f"❄️ **HÀNG TỒN ĐỌNG (Trên 90 ngày)**\n"
            plan += f"_(Tồn > 5 cuốn nhưng không phát sinh doanh số - Cần giải phóng vốn)_\n"
            for p in report['dead_stock'][:5]:
                 plan += f"- {p['title']} (Tồn: {p.get('inventory_quantity', 0)})\n"
            plan += "👉 **Hành động**: \n"
            plan += "   + Tạo Combo 'Sách Mù' hoặc 'Xả kho từ 19k'.\n"
            plan += "   + Tặng kèm cho đơn hàng giá trị cao.\n\n"

        # 3. ABC Analysis Highlights
        plan += f"🌟 **NHÓM A - Sản phẩm Chủ lực ({len(report['group_a'])} sp)**\n"
        for p in report['group_a'][:3]:
            plan += f"- {p['title']} (Bán: {p['current_sales']})\n"
        
        # Missing Data
        if report.get("missing_images"):
            plan += f"\n⚠️ **Cảnh báo**: Có {len(report['missing_images'])} sp thiếu ảnh.\n"

        # Send Email Report
        if self.notifier:
            html_plan = plan.replace("\n", "<br>")
            self.notifier.send_report("📊 [Inventory] Báo cáo Tồn kho Sâu", f"<html><body>{html_plan}</body></html>")

        return plan

    def analyze_stock(self):
        """
        Enhanced analysis including Dead Stock & Fast Movers.
        """
        print(f"🤖 [Inventory Agent] Starting Deep Inventory Analysis...")
        
        variants = self.hrv.get_all_products()
        if not variants: return {"error": "No products found"}

        # Fetch sales for 30 and 90 days
        sku_sales_30 = self.hrv.get_variant_sales(days=30)
        sku_sales_90 = self.hrv.get_variant_sales(days=90)
        
        processed_items = []
        for v in variants:
            sku = v.get('sku', '').upper()
            v['current_sales'] = sku_sales_30.get(sku, 0)
            processed_items.append(v)
                
        sorted_products = sorted(processed_items, key=lambda x: x['current_sales'], reverse=True)
        
        # ABC Classification
        total_items = len(sorted_products)
        top_20_count = max(1, int(total_items * 0.2))
        group_a = sorted_products[:top_20_count]
        remaining = sorted_products[top_20_count:]
        group_c = [p for p in remaining if p['current_sales'] == 0]
        group_b = [p for p in remaining if p['current_sales'] > 0]

        # Deep Analysis
        dead_stock = self.identify_dead_stock(variants, sku_sales_90)
        fast_movers = self.identify_fast_movers(variants, sku_sales_30)

        return {
            "total_scanned": total_items,
            "group_a": group_a,
            "group_b": group_b,
            "group_c": group_c,
            "dead_stock": dead_stock,
            "fast_movers": fast_movers,
            "missing_images": [p for p in processed_items if not p.get('images')]
        }

if __name__ == "__main__":
    agent = InventoryAnalystAgent()
    # Mocking data for test if no API
    # ...
    try:
        analysis = agent.analyze_stock()
        print(agent.generate_action_plan(analysis))
    except Exception as e:
        print(f"Error: {e}")
