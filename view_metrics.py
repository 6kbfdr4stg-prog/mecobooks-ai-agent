import json
import os
from collections import Counter
from datetime import datetime

def analyze_logs(log_file="logs/app.jsonl"):
    if not os.path.exists(log_file):
        print(f"File not found: {log_file}")
        return

    stats = {
        "total_queries": 0,
        "responses": 0,
        "author_inferences": 0,
        "conversions": 0,
        "errors": 0,
        "top_searches": Counter(),
        "users": set()
    }

    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                meta = data.get("metadata", {})
                event = meta.get("event")

                if event == "USER_QUERY":
                    stats["total_queries"] += 1
                    stats["users"].add(meta.get("user_id"))
                    stats["top_searches"][meta.get("query")] += 1
                
                elif event == "BOT_RESPONSE":
                    stats["responses"] += 1
                
                elif event == "CONVERSION":
                    stats["conversions"] += 1
                
                if data.get("level") == "ERROR":
                    stats["errors"] += 1
                
                if data.get("message") == "AI Inferred Author":
                    stats["author_inferences"] += 1

            except Exception:
                continue

    print("\n" + "="*40)
    print("📊 BÁO CÁO HIỆU SUẤT CHATBOT")
    print("="*40)
    print(f"📅 Ngày báo cáo: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"👥 Tổng số khách: {len(stats['users'])}")
    print(f"💬 Tổng số tin nhắn: {stats['total_queries']}")
    print(f"✅ Phản hồi thành công: {stats['responses']}")
    print(f"🤖 AI hỗ trợ tìm tác giả: {stats['author_inferences']} lần")
    print(f"💰 Đơn hàng thành công (Conversion): {stats['conversions']}")
    print(f"⚠️ Lỗi hệ thống: {stats['errors']}")
    
    print("\n🔍 TOP TỪ KHÓA TÌM KIẾM:")
    for term, count in stats["top_searches"].most_common(5):
        print(f"- {term}: {count} lần")
    print("="*40 + "\n")

if __name__ == "__main__":
    analyze_logs()
