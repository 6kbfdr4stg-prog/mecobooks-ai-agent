import os
import sys
import json
from collections import Counter

# Add parent dir to path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_service import LLMService
from woocommerce_client import WooCommerceClient

class StrategicAnalystAgent:
    def __init__(self):
        self.woo = WooCommerceClient()
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

if __name__ == "__main__":
    analyst = StrategicAnalystAgent()
    # Mock inventory report for testing
    mock_report = "Nhóm A (Bán chạy): Sách kinh doanh (Tồn thấp). Nhóm C (Tồn kho): Sách văn học cũ (Tồn cao)."
    print("--- STRATEGIC ANALYSIS ---")
    print(analyst.generate_growth_strategy(mock_report))
