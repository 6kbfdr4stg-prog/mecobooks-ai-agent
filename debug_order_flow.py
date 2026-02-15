
import sys
import os

# Add parent path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_agents.sales_support import SalesSupportAgent

def test_order_flow():
    print("🤖 Initializing Sales Agent...")
    try:
        agent = SalesSupportAgent()
    except Exception as e:
        print(f"❌ Error initializing agent: {e}")
        return

    user_id = "test_user_001"
    
    # 0. Test RAG / Knowledge Base
    print("\n[Step 0] User asks general question: 'Shop ở đâu vậy?'")
    response = agent.handle_customer_query("Shop ở đâu vậy?", user_id=user_id)
    print(f"Agent: {response}")

    # 1. User wants to buy a book
    print("\n[Step 1] User asks to buy 'Nhà Giả Kim'")
    response = agent.handle_customer_query("Tôi muốn mua sách Nhà Giả Kim", user_id=user_id)
    # ... existing flow ...
    print(f"Agent: {response}")
    
    # 2. User provides name
    print("\n[Step 2] User provides Name: 'Nguyễn Văn Test'")
    response = agent.handle_customer_query("Nguyễn Văn Test", user_id=user_id)
    print(f"Agent: {response}")

    # 3. User provides Phone
    print("\n[Step 3] User provides Phone: '0909123456'")
    response = agent.handle_customer_query("0909123456", user_id=user_id)
    print(f"Agent: {response}")

    # 4. User provides Address
    print("\n[Step 4] User provides Address: '123 Test Street, HCM'")
    response = agent.handle_customer_query("123 Test Street, HCM", user_id=user_id)
    print(f"Agent: {response}")

    # 5. User Confirms
    print("\n[Step 5] User Confirms: 'Ok chốt đơn'")
    response = agent.handle_customer_query("Ok chốt đơn", user_id=user_id)
    print(f"Agent: {response}")

    # 6. User Tracking
    # Extract order id from prev step if possible, hardcode for now or regex
    import re
    match = re.search(r'#(\d+)', response)
    if match:
        order_id = match.group(1)
        print(f"\n[Step 6] User tracks order #{order_id}")
        
        # 6a. Ask to track
        res1 = agent.handle_customer_query("Kiểm tra đơn hàng", user_id=user_id)
        print(f"Agent: {res1}")
        
        # 6b. Provide ID
        res2 = agent.handle_customer_query(order_id, user_id=user_id)
        print(f"Agent: {res2}")

if __name__ == "__main__":
    test_order_flow()
