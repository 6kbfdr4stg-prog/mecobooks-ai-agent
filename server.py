from fastapi import FastAPI, HTTPException, Request, Response, Form, File, UploadFile, BackgroundTasks, Body, Depends, status
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from ai_agents.sales_support import SalesSupportAgent
# Removed SQLAlchemy imports
from database import get_db_connection, init_db
import uvicorn
import os
import requests
import glob
import sqlite3
from datetime import datetime

# Initialize Database
init_db()

app = FastAPI(title="Haravan AI Chatbot API")
security = HTTPBasic()

# Authentication Dependency
def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = os.environ.get("ADMIN_USER", "admin")
    correct_password = os.environ.get("ADMIN_PASSWORD", "admin")
    
    import secrets
    is_correct_username = secrets.compare_digest(credentials.username, correct_username)
    is_correct_password = secrets.compare_digest(credentials.password, correct_password)
    
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

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

def sync_reports_to_db():
    """One-time sync of Markdown files to Database."""
    report_dir = "reports"
    if not os.path.exists(report_dir):
        return
        
    conn = get_db_connection()
    c = conn.cursor()
    
    for filepath in glob.glob(os.path.join(report_dir, "*.md")):
        filename = os.path.basename(filepath)
        if filename == "README.md":
            continue
            
        # Check if already exists in DB
        c.execute("SELECT id FROM reports WHERE agent_name = ?", (filename,))
        if c.fetchone():
            continue
            
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Infer agent name and time from filename/metadata
        # simplistic mapping for now, using filename as key identifier
        stat = os.stat(filepath)
        created_at = datetime.fromtimestamp(stat.st_mtime)
        
        c.execute("INSERT INTO reports (agent_name, report_type, content, created_at) VALUES (?, ?, ?, ?)",
                  (filename, "markdown", content, created_at))
    
    conn.commit()
    conn.close()

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
    # Sync Reports
    try:
        sync_reports_to_db()
        print("✅ [System] Reports synced to Database.")
    except Exception as e:
        print(f"⚠️ [System] Report sync failed: {e}")

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

# Dependency - Removed get_db as it's no longer needed with direct sqlite3 connections

@app.post("/run-agent")
async def run_agent_endpoint(data: dict = Body(...)):
    """
    Endpoint for n8n/External triggers. Publicly accessible (or protect if needed).
    """
    agent_name = data.get("agent")
    
    if agent_name in ["content_creator", "inventory_analyst", "strategic_analyst", "integrity_manager", "market_research"]:
        # Dynamic class loading is risky, stick to explicit map or simple if-else for safety
        if agent_name == "content_creator":
            from ai_agents.content_creator import ContentCreatorAgent
            agent = ContentCreatorAgent()
        elif agent_name == "inventory_analyst":
            from ai_agents.inventory_analyst import InventoryAnalystAgent
            agent = InventoryAnalystAgent()
        elif agent_name == "strategic_analyst":
            from ai_agents.strategic_analyst import StrategicAnalystAgent
            agent = StrategicAnalystAgent()
        elif agent_name == "integrity_manager":
            from ai_agents.integrity_manager import IntegrityManagerAgent
            agent = IntegrityManagerAgent()
        elif agent_name == "market_research":
            from ai_agents.market_research import MarketResearchAgent
            agent = MarketResearchAgent()
            
        threading.Thread(target=agent.run).start()
        return {"status": "started", "agent": agent_name}
        
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

@app.get("/api/reports")
async def list_reports(username: str = Depends(get_current_username)):
    """List all saved reports from Database."""
    conn = get_db_connection()
    c = conn.cursor()
    reports = c.execute("SELECT * FROM reports ORDER BY created_at DESC").fetchall()
    
    results = []
    for r in reports:
        # r is sqlite3.Row, access by name
        results.append({
            "id": r["id"],
            "filename": r["agent_name"] + ("" if ".md" in r["agent_name"] else ".md"), # Keep compatible with old filename usage
            "name": r["agent_name"].replace("_latest.md", "").replace(".md", "").replace("_", " ").title(),
            "modified": r["created_at"],
            "size_kb": round(len(r["content"])/1024, 1)
        })
    conn.close()
    return {"reports": results}

@app.get("/api/reports/{report_id}")
async def get_report_by_id(report_id: str, username: str = Depends(get_current_username)):
    """Read content of a specific report using ID or Filename (legacy support)."""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Try by ID first
    if report_id.isdigit():
        report = c.execute("SELECT * FROM reports WHERE id = ?", (int(report_id),)).fetchone()
    else:
        # Legacy/Filename fallback
        report = c.execute("SELECT * FROM reports WHERE agent_name = ?", (report_id,)).fetchone()
        
    conn.close()
    
    if not report:
         raise HTTPException(status_code=404, detail="Report not found")
         
    return {
        "filename": report["agent_name"],
        "modified": report["created_at"],
        "content": report["content"]
    }

@app.get("/api/stats")
async def get_dashboard_stats(username: str = Depends(get_current_username)):
    """
    Returns dashboard statistics (Protected).
    """
    import psutil
    import asyncio
    
    try:
        # 1. System Health (Local)
        try:
            import psutil
            cpu_usage = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            mem_percent = memory.percent
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
        except (ImportError, AttributeError, Exception):
            # Fallback if psutil is missing or fails
            cpu_usage = 0
            mem_percent = 0
            disk_percent = 0
        
        system_health = {
            "cpu": cpu_usage,
            "memory": mem_percent,
            "disk": disk_percent
        }
        
        # 2. WooCommerce Stats (Remote)
        def fetch_woo_stats():
            from woocommerce_client import WooCommerceClient
            woo = WooCommerceClient()
            sales_month = woo.get_sales_report(period="month")
            return {
                "sales_total": sales_month.get("total_sales", 0),
                "orders_count": sales_month.get("total_orders", 0),
                "new_customers": sales_month.get("total_customers", 0)
            }
            
        woo_stats = await asyncio.to_thread(fetch_woo_stats)
        
        return {
            "system": system_health,
            "business": woo_stats
        }
    except Exception as e:
        print(f"Stats Error: {e}")
        return {"error": str(e)}

@app.post("/run-agent-sync/{agent_name}")
async def run_agent_sync(agent_name: str, username: str = Depends(get_current_username)):
    """
    Runs an agent synchronously and saves result to DB.
    """
    import asyncio

    def _run_agent_logic(name):
        try:
            result = None
            if name == "content_creator":
                from ai_agents.content_creator import ContentCreatorAgent
                agent = ContentCreatorAgent()
                result = agent.run()
            elif name == "inventory_analyst":
                from ai_agents.inventory_analyst import InventoryAnalystAgent
                agent = InventoryAnalystAgent()
                result = agent.run()
            elif name == "market_research":
                from ai_agents.market_research import MarketResearchAgent
                agent = MarketResearchAgent()
                result = agent.run()
            elif name == "integrity_manager":
                from ai_agents.integrity_manager import IntegrityManagerAgent
                agent = IntegrityManagerAgent()
                # Integrity manager returns a path
                report_path = agent.run()
                if os.path.exists(report_path):
                     with open(report_path, "r", encoding="utf-8") as f:
                        result = f.read()
                else:
                    result = "Report generation failed."
            else:
                 raise HTTPException(status_code=400, detail="Unknown agent")

            return result # Return raw content or path depending on agent
        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"Error: {str(e)}"

    # Run agent
    content = await asyncio.to_thread(_run_agent_logic, agent_name)
    
    # Save to Database
    if content and isinstance(content, str):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO reports (agent_name, report_type, content, created_at) VALUES (?, ?, ?, ?)",
                  (f"{agent_name}_{datetime.now().strftime('%Y%m%d%H%M')}.md", "markdown", content, datetime.utcnow()))
        conn.commit()
        conn.close()

    return {"status": "success", "agent": agent_name, "output": content}

@app.get("/verify", response_class=HTMLResponse)
async def verification_dashboard(username: str = Depends(get_current_username)):
    """
    Serves the Verification Dashboard (Protected).
    """
    try:
        with open("templates/verification.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Verification Dashboard Not Found</h1>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port)
