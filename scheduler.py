
import time
import schedule
import os
import sys

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_agents.content_creator import ContentCreatorAgent
from ai_agents.inventory_analyst import InventoryAnalystAgent
from ai_agents.email_marketing import EmailMarketingAgent
from ai_agents.strategic_analyst import StrategicAnalystAgent
from ai_agents.integrity_manager import IntegrityManagerAgent
from ai_agents.market_research import MarketResearchAgent

def job_integrity_check():
    print("🛡️ [Scheduler] Running System Integrity Check...")
    try:
        agent = IntegrityManagerAgent()
        agent.run()
    except Exception as e:
        print(f"❌ Integrity Check Failed: {e}")

def job_strategic_analysis():
    print("⏰ [Scheduler] Triggering Strategic Analysis (Agent 4)...")
    try:
        inventory_agent = InventoryAnalystAgent()
        report = inventory_agent.analyze_stock()
        
        strategic_agent = StrategicAnalystAgent()
        strategy = strategic_agent.generate_growth_strategy(report)
        
        print("\n=== 🚀 CHIẾN LƯỢC TĂNG TRƯỞNG TUẦN TỚI ===")
        print(strategy)
        print("==========================================\n")
        
        # In a real app, send this to Telegram/Zalo of the owner
    except Exception as e:
        print(f"❌ Strategic Analysis Failed: {e}")

def job_email_marketing():
    print("⏰ [Scheduler] Triggering Daily Email Marketing...")
    try:
        agent = EmailMarketingAgent()
        agent.run_daily_campaign()
    except Exception as e:
        print(f"❌ Email Marketing Failed: {e}")

def job_create_content():
    print("⏰ [Scheduler] Triggering Daily Content Creation (Agent 1 & 2)...")
    try:
        # First, check inventory to see what to promote
        inventory_agent = InventoryAnalystAgent()
        report = inventory_agent.analyze_stock() # Standard ABC Analysis
        
        # Simple Logic: Promote one 'Nhóm A' and one 'Nhóm C'
        # For now, let ContentCreator pick but give it the report as context
        agent = ContentCreatorAgent()
        result = agent.generate_daily_content()
        
        print(f"✅ Content Generated: {result.get('caption', '')[:50]}...")
        agent.send_to_webhook(result)

    except Exception as e:
        print(f"❌ Content Generation Failed: {e}")

def job_analyze_inventory():
    print("⏰ [Scheduler] Triggering Weekly Inventory Analysis (Agent 3)...")
    try:
        agent = InventoryAnalystAgent()
        report = agent.analyze_stock()
        plan = agent.generate_action_plan(report)
        print("✅ Inventory Analysis Complete.")
        print(plan)
    except Exception as e:
        print(f"❌ Inventory Analysis Failed: {e}")

def job_market_research():
    print("⏰ [Scheduler] Running 3-day Market Research...")
    try:
        agent = MarketResearchAgent()
        agent.run()
    except Exception as e:
        print(f"❌ Market Research Failed: {e}")

# Define Schedule
# Production Schedule (Hanoi Time GMT+7 -> UTC)
schedule.every().day.at("04:00").do(job_create_content) # 11:00 AM VN
schedule.every().day.at("13:00").do(job_create_content) # 20:00 PM VN

schedule.every().day.at("03:00").do(job_email_marketing) # 10:00 AM VN

schedule.every().monday.at("01:00").do(job_analyze_inventory) # 08:00 AM VN
schedule.every().sunday.at("14:00").do(job_strategic_analysis) # 21:00 PM VN Sunday prep for week
schedule.every(3).days.at("02:00").do(job_market_research) # 09:00 AM VN every 3 days
schedule.every().hour.do(job_integrity_check) # Self-healing check every hour

# Demo Schedule (Run immediately for first loop then every 10 mins?)
# schedule.every(10).minutes.do(job_create_content)

if __name__ == "__main__":
    print("🚀 AI Agent Scheduler Started...")
    print("   - Daily Content at 09:00")
    print("   - Weekly Inventory on Monday at 08:00")

    while True:
        schedule.run_pending()
        time.sleep(60)
