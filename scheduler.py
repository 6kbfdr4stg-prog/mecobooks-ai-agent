
import time
import schedule
import os
import sys

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_agents.content_creator import ContentCreatorAgent
from ai_agents.inventory_analyst import InventoryAnalystAgent
from ai_agents.email_marketing import EmailMarketingAgent

def job_email_marketing():
    print("⏰ [Scheduler] Triggering Daily Email Marketing...")
    try:
        agent = EmailMarketingAgent()
        agent.run_daily_campaign()
    except Exception as e:
        print(f"❌ Email Marketing Failed: {e}")

def job_create_content():
    print("⏰ [Scheduler] Triggering Daily Content Creation...")
    try:
        agent = ContentCreatorAgent()
        # In a real deployed env, you might post this to an API or save to DB.
        # Here we just print it.
        result = agent.generate_daily_content()
        print(f"✅ Content Generated: {result.get('caption', '')[:50]}...")
        
        # Post via Webhook (Make/n8n)
        agent.send_to_webhook(result)

    except Exception as e:
        print(f"❌ Content Generation Failed: {e}")

def job_analyze_inventory():
    print("⏰ [Scheduler] Triggering Weekly Inventory Analysis...")
    try:
        agent = InventoryAnalystAgent()
        report = agent.analyze_stock()
        plan = agent.generate_action_plan(report)
        print("✅ Inventory Analysis Complete.")
        print(plan)
        # Could email this plan to admin
    except Exception as e:
        print(f"❌ Inventory Analysis Failed: {e}")

# Define Schedule
# For demo purposes, we can run every minute to show it works, 
# but in production, uncomment the real times.

# Production Schedule
# Converting Hanoi Time (GMT+7) to UTC for Render Server
schedule.every().day.at("04:00").do(job_create_content) # 11:00 AM VN
schedule.every().day.at("13:00").do(job_create_content) # 20:00 PM VN

schedule.every().day.at("03:00").do(job_email_marketing) # 10:00 AM VN

schedule.every().monday.at("01:00").do(job_analyze_inventory) # 08:00 AM VN

# Demo Schedule (Run immediately for first loop then every 10 mins?)
# schedule.every(10).minutes.do(job_create_content)

print("🚀 AI Agent Scheduler Started...")
print("   - Daily Content at 09:00")
print("   - Weekly Inventory on Monday at 08:00")

# Run once on startup to verify (Optional)
# job_create_content() # Uncomment to run immediately on startup
# job_analyze_inventory()

while True:
    schedule.run_pending()
    time.sleep(60)
