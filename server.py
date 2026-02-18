from fastapi import FastAPI, HTTPException, Request, Response, Form, File, UploadFile, BackgroundTasks, Body
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ai_agents.sales_support import SalesSupportAgent
import uvicorn
import os
import requests

app = FastAPI(title="Haravan AI Chatbot API")

# Enable CORS for WordPress
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# --- Background Scheduler Integration ---
import threading
import time
import schedule
import scheduler  # This imports the job definitions from scheduler.py

def run_scheduler_loop():
    print("⏳ [Background] Scheduler loop started...")
    while True:
        try:
            schedule.run_pending()
        except Exception as e:
            print(f"❌ [Background] Scheduler Error: {e}")
        time.sleep(60)

@app.on_event("startup")
async def start_scheduler():
    # Start the scheduler in a separate daemon thread
    t = threading.Thread(target=run_scheduler_loop, daemon=True)
    t.start()
    print("✅ [System] Scheduler thread launched.")
# ----------------------------------------

from fastapi.staticfiles import StaticFiles
# Mount static directory for videos
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Chatbot (Agent)
try:
    bot = SalesSupportAgent()
except Exception as e:
    print(f"Failed to initialize chatbot: {e}")
    bot = None

class ChatResponse(BaseModel):
    response: str
    
class ChatRequest(BaseModel):
    message: str
    user_id: str = "guest"

# Facebook Config
FB_VERIFY_TOKEN = os.environ.get("FB_VERIFY_TOKEN", "my_secure_verify_token")
FB_PAGE_ACCESS_TOKEN = os.environ.get("FB_PAGE_ACCESS_TOKEN")

@app.post("/run-agent")
async def run_agent_endpoint(data: dict = Body(...)):
    """
    Endpoint for n8n/External triggers to run specific agents.
    Ex: {"agent": "content_creator"}
    """
    agent_name = data.get("agent")
    
    # 1. Content Creator
    if agent_name == "content_creator":
        from ai_agents.content_creator import ContentCreatorAgent
        agent = ContentCreatorAgent()
        # Run in background to avoid timeout
        import threading
        threading.Thread(target=agent.run).start()
        return {"status": "started", "agent": "content_creator"}
        
    # 2. Inventory Analyst
    elif agent_name == "inventory_analyst":
        from ai_agents.inventory_analyst import InventoryAnalystAgent
        agent = InventoryAnalystAgent()
        import threading
        threading.Thread(target=agent.run).start()
        return {"status": "started", "agent": "inventory_analyst"}
        
    # 3. Strategic Analyst
    elif agent_name == "strategic_analyst":
        from ai_agents.strategic_analyst import StrategicAnalystAgent
        agent = StrategicAnalystAgent()
        import threading
        threading.Thread(target=agent.run).start()
        return {"status": "started", "agent": "strategic_analyst"}
        
    # 4. Integrity Manager
    elif agent_name == "integrity_manager":
        from ai_agents.integrity_manager import IntegrityManagerAgent
        agent = IntegrityManagerAgent()
        import threading
        threading.Thread(target=agent.run).start()
        return {"status": "started", "agent": "integrity_manager"}
    
    # 5. Market Research
    elif agent_name == "market_research":
        from ai_agents.market_research import MarketResearchAgent
        agent = MarketResearchAgent()
        import threading
        threading.Thread(target=agent.run).start()
        return {"status": "started", "agent": "market_research"}
        
    return {"status": "error", "message": "Unknown agent"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Haravan AI Chatbot is running"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    message: str = Form(None), 
    user_id: str = Form("guest"),
    file: UploadFile = File(None)
):
    # Support both Form data (for file upload compat) and JSON if needed in future
    # Currently Widget uses FormData
    
    if not message and not file:
         raise HTTPException(status_code=400, detail="Message or File required")

    if not bot:
        raise HTTPException(status_code=500, detail="Chatbot not initialized properly")
    
    try:
        image_data = None
        if file:
            print(f"Received file: {file.filename}")
            image_data = await file.read()
            
        response_text = bot.process_message(message or "", image_data=image_data, user_id=user_id)
        return {"response": response_text}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/webhook")
async def fb_verify(request: Request):
    """
    Facebook Verification Endpoint.
    """
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == FB_VERIFY_TOKEN:
            print("WEBHOOK_VERIFIED")
        if mode == "subscribe" and token == FB_VERIFY_TOKEN:
            print("WEBHOOK_VERIFIED")
            return Response(content=challenge, media_type="text/plain")
        else:
            raise HTTPException(status_code=403, detail="Verification failed")
    return {"status": "waiting_for_facebook"}

@app.post("/webhook")
async def fb_webhook(request: Request):
    """
    Facebook Message Handling Endpoint.
    """
    body = await request.json()
    
    if body.get("object") == "page":
        for entry in body.get("entry", []):
            for event in entry.get("messaging", []):
                if event.get("message"):
                    sender_id = event["sender"]["id"]
                    message_text = event["message"].get("text")
                    
                    if message_text or event["message"].get("attachments"):
                        # Process message with Chatbot
                        response_data = "Xin lỗi, chatbot chưa sẵn sàng."
                        if bot:
                            try:
                                # Extract image URL if present
                                image_url = None
                                attachments = event["message"].get("attachments", [])
                                if attachments:
                                    for att in attachments:
                                        if att["type"] == "image":
                                            image_url = att["payload"]["url"]
                                            break
                                
                                # Use platform="facebook" to get structured data
                                response_data = bot.process_message(message_text, platform="facebook", image_url=image_url)
                            except Exception as e:
                                print(f"Bot Error: {e}")
                                response_data = "Có lỗi xảy ra khi xử lý tin nhắn."

                        # Send response back to Facebook
                        send_fb_message(sender_id, response_data)
        
        return Response(content="EVENT_RECEIVED", status_code=200)
    else:
        raise HTTPException(status_code=404, detail="Not a page event")

def send_fb_message(recipient_id, message_data):
    """
    Send text or structured message back to Facebook User.
    """
    if not FB_PAGE_ACCESS_TOKEN:
        print("Missing FB_PAGE_ACCESS_TOKEN")
        return

    url = f"https://graph.facebook.com/v22.0/me/messages?access_token={FB_PAGE_ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "recipient": {"id": recipient_id}
    }

    if isinstance(message_data, str):
         payload["message"] = {"text": message_data}
    elif isinstance(message_data, list):
        # Generic Template (Carousel)
        payload["message"] = {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": message_data
                }
            }
        }
    else:
        print(f"Unknown message type: {type(message_data)}")
        return
    
    try:
        r = requests.post(url, headers=headers, json=payload)
        if r.status_code != 200:
            print(f"Failed to send message: {r.text}")
    except Exception as e:
        print(f"Error sending message: {e}")

@app.get("/widget", response_class=HTMLResponse)
async def get_widget():
    """
    Serves the Chat Widget HTML.
    """
    try:
        with open("chat_widget.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Widget file not found."

@app.get("/widget-loader", response_class=Response)
async def get_widget_loader():
    """
    Serves the Widget Loader JS.
    """
    try:
        with open("widget_loader.js", "r", encoding="utf-8") as f:
            return Response(content=f.read(), media_type="application/javascript")
    except FileNotFoundError:
        return Response(content="console.error('Widget loader not found');", media_type="application/javascript")

@app.get("/feed.xml")
async def get_feed():
    """
    Generates and returns the Google Shopping Product Feed.
    """
    from product_feed import generate_xml_feed
    try:
        xml_content = generate_xml_feed()
        return Response(content=xml_content, media_type="application/xml")
    except Exception as e:
        print(f"Feed Generation Error: {e}")
        return Response(content=f"<error>{str(e)}</error>", media_type="application/xml", status_code=500)

# ... existing imports ...
import threading
import time
import schedule
from scheduler import job_create_content, job_email_marketing, job_analyze_inventory

# Define Schedule inside server or import from scheduler.py
# If we import from scheduler.py, we need to make sure scheduler.py defines the schedule but doesn't run the loop immediately on import.
# Let's just redefine the schedule here or rely on scheduler.py's definitions if it was a module.
# Actually, scheduler.py has a 'while True' at the bottom. We should remove that or wrap it.
# Ideally, we should refactor scheduler.py to be importable.
# check scheduler.py content again. It has `while True` at the end. Importing it might block.
# Let's adding a check in scheduler.py first, but since we can't edit two files in one step easily if we want to be safe,
# I will just replicate the schedule logic here for simplicity and reliability in this context, 
# OR I will edit scheduler.py to only run if __name__ == "__main__".

# Strategy: I'll edit scheduler.py next. For now, let's prepare server.py to IMPORT it.
# Actually, if I modify scheduler.py to not block on import, I can import it here.

def run_scheduler():
    from scheduler import job_create_content, job_email_marketing, job_analyze_inventory, job_market_research
    import schedule
    
    # Redefine schedule here to be safe and explicit
    schedule.every().day.at("04:00").do(job_create_content) # 11:00 AM VN
    schedule.every().day.at("13:00").do(job_create_content) # 20:00 PM VN
    schedule.every().day.at("03:00").do(job_email_marketing) # 10:00 AM VN
    schedule.every().monday.at("01:00").do(job_analyze_inventory) # 08:00 AM VN
    schedule.every(3).days.at("02:00").do(job_market_research) # 09:00 AM VN every 3 days
    
    print("🚀 [Server] Scheduler thread started...")
    while True:
        schedule.run_pending()
        time.sleep(60)

@app.on_event("startup")
def startup_event():
    # Start scheduler in a separate thread
    t = threading.Thread(target=run_scheduler, daemon=True)
    t.start()
    print("🚀 SERVER RESTARTED WITH FIX v3 - VERIFICATION DASHBOARD")

@app.post("/debug/trigger-content")
async def trigger_content(background_tasks: BackgroundTasks):
    """
    Manually trigger content generation (for testing).
    """
    from scheduler import job_create_content
    background_tasks.add_task(job_create_content)
    return {"status": "triggered", "message": "Content generation started in background"}

@app.get("/debug/videos")
async def list_videos():
    """
    List all generated videos.
    """
    video_dir = "static/videos"
    if not os.path.exists(video_dir):
        return {"videos": []}
    
    files = os.listdir(video_dir)
    video_files = [f for f in files if f.endswith(".mp4")]
    return {
        "count": len(video_files),
        "params": [f"https://mecobooks-ai.onrender.com/static/videos/{f}" for f in video_files]
    }

@app.get("/test-email")
async def test_email_endpoint(email: str = None):
    """
    Manually trigger a test email to verify SMTP settings.
    Usage: /test-email?email=user@example.com (or default to owner)
    """
    from utils.email_notifier import EmailNotifier
    notifier = EmailNotifier()
    try:
        subject = "🧪 [Manual Test] Kiểm tra hệ thống Email từ Server"
        body = """
        <html><body>
        <h2 style="color: green;">Email Test Thành Công!</h2>
        <p>Đây là email được gửi thủ công từ endpoint <code>/test-email</code> trên Render.</p>
        <p>Hệ thống gửi nhận hoạt động tốt.</p>
        </body></html>
        """
        # Run in thread to not block
        import threading
        t = threading.Thread(target=notifier.send_report, args=(subject, body, email))
        t.start()
        
        return {"status": "sent", "message": "Email is being sent in background."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/run-agent-sync/{agent_name}")
async def run_agent_sync(agent_name: str):
    """
    Runs an agent synchronously and returns the result/report.
    """
    try:
        result = None
        
        if agent_name == "content_creator":
            from ai_agents.content_creator import ContentCreatorAgent
            agent = ContentCreatorAgent()
            result = agent.run()
            
        elif agent_name == "inventory_analyst":
            from ai_agents.inventory_analyst import InventoryAnalystAgent
            agent = InventoryAnalystAgent()
            result = agent.run()
            
        elif agent_name == "market_research":
            from ai_agents.market_research import MarketResearchAgent
            agent = MarketResearchAgent()
            result = agent.run()
            
        elif agent_name == "integrity_manager":
            from ai_agents.integrity_manager import IntegrityManagerAgent
            agent = IntegrityManagerAgent()
            report_path = agent.run()
            # Read the report content
            if os.path.exists(report_path):
                with open(report_path, "r", encoding="utf-8") as f:
                    result = {"report_path": report_path, "content": f.read()}
            else:
                result = {"report_path": report_path, "content": "Report file not found."}
        
        else:
             raise HTTPException(status_code=400, detail="Unknown agent")

        return {"status": "success", "agent": agent_name, "output": result}

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

@app.get("/verify", response_class=HTMLResponse)
async def verification_dashboard():
    """
    Serves the Verification Dashboard.
    """
    try:
        with open("templates/verification.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Verification Dashboard Not Found</h1><p>Please ensure templates/verification.html exists.</p>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True)
