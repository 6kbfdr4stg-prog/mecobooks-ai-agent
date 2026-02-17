
import sys
import os

# Add parent path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_agents.sales_support import SalesSupportAgent

def test_sales_agent():
    print("🤖 Initializing Sales Agent...")
    try:
        agent = SalesSupportAgent()
    except Exception as e:
        print(f"❌ Error initializing agent: {e}")
        return

    # Test Queries
    queries = [
        "Tiệm có sách Nhà Giả Kim không?",
        "Sách Đắc Nhân Tâm giá bao nhiêu?",
        "Tôi muốn mua sách Mùa Tôm"
    ]

    print("\n💬 --- STARTING TEST CONVERSATIONS ---\n")
    for q in queries:
        print(f"User: {q}")
        response = agent.handle_customer_query(q)
        print(f"Agent: {response}")
        print("-" * 50)

if __name__ == "__main__":
    test_sales_agent()
