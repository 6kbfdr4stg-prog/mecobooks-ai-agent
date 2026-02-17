import time
import random
import traceback
import sys

print("DEBUG: Script started")
try:
    from ai_agents.sales_support import SalesSupportAgent
    print("DEBUG: Import successful")
except Exception as e:
    print(f"DEBUG: Import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

def simulate_traffic():
    agent = SalesSupportAgent()
    
    test_queries = [
        # Search & Sales
        "Tìm cuốn Nhà Giả Kim",
        "Có sách Dạy con làm giàu không?",
        "Giá cuốn Đắc Nhân Tâm bao nhiêu?",
        "Mua cuốn Harry Potter",
        "Tìm sách abcxyz không tồn tại", # Should trigger Not Found
        
        # Order Tracking
        "Kiểm tra đơn hàng #12345",
        "Tra cứu đơn 99999", # Should fail
        "Tình trạng đơn hàng #25310", # Should succeed if exists
        
        # Consulting / Chat
        "Chào shop",
        "Shop ở đâu vậy?",
        "Tư vấn cho mình sách kinh doanh",
        
        # Typo / Hard queries
        "Tim cuon Nha Gia Kim",
        "Day con lam giau",
        "Có truyện tranh Đoremon không"
    ]
    
    print("🚀 Starting Traffic Simulation...")
    print(f"Testing {len(test_queries)} queries...")
    
    success_count = 0
    errors = 0
    start_time = time.time()
    
    for i, query in enumerate(test_queries):
        print(f"\n[{i+1}/{len(test_queries)}] User: {query}")
        
        try:
            t0 = time.time()
            # Simulate different users
            user_id = f"user_{random.randint(1000, 9999)}"
            response = agent.handle_customer_query(query, user_id=user_id)
            duration = time.time() - t0
            
            print(f"🤖 Bot ({duration:.2f}s): {response[:100]}...")
            success_count += 1
            
            # Random delay
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            errors += 1
            
    total_time = time.time() - start_time
    print("\n------------------------------------------------")
    print(f"✅ Completed in {total_time:.2f}s")
    print(f"Success: {success_count} | Errors: {errors}")
    print("Check 'logs/app.jsonl' for details.")

if __name__ == "__main__":
    simulate_traffic()
