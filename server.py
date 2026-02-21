from fastapi import FastAPI, HTTPException, Depends, Request, Response, Form, File, UploadFile, Body, BackgroundTasks, status
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from ai_agents.sales_support import SalesSupportAgent
# Removed SQLAlchemy imports
from database import get_db_connection, init_db
from utils.event_manager import event_manager
import uvicorn
import asyncio
import os
import requests
import glob
import sqlite3
import json
from datetime import datetime
from config import get_now_hanoi

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
# Import job definitions from scheduler.py to register them with the global 'schedule' object
import scheduler 

def run_scheduler_background():
    """Single background thread for the scheduler."""
    print("🚀 [System] Scheduler thread launched. Monitoring jobs...")
    while True:
        try:
            schedule.run_pending()
        except Exception as e:
            print(f"❌ [Scheduler Error] {e}")
            try:
                from ai_agents.telegram_client import send_telegram_message
                send_telegram_message(f"🚨 <b>Scheduler Error</b>\n\n<code>{str(e)}</code>")
            except: pass
        time.sleep(60)

def sync_reports_to_db():
    """One-time sync of Markdown files to Database."""
    report_dirs = ["reports", "reports_v2"]
    
    conn = get_db_connection()
    c = conn.cursor()
    
    for report_dir in report_dirs:
        if not os.path.exists(report_dir):
            continue
            
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
            # Using Hanoi time for modification time conversion
            stat = os.stat(filepath)
            from datetime import timezone, timedelta
            hanoi_offset = timezone(timedelta(hours=7))
            created_at = datetime.fromtimestamp(stat.st_mtime, hanoi_offset)
            
            c.execute("INSERT INTO reports (agent_name, report_type, content, created_at) VALUES (?, ?, ?, ?)",
                      (filename, "markdown", content, created_at))
    
    conn.commit()
    conn.close()


@app.on_event("startup")
async def startup_event():
    # 1. Sync Reports
    try:
        sync_reports_to_db()
        print("✅ [System] Reports synced to Database.")
    except Exception as e:
        print(f"⚠️ [System] Report sync failed: {e}")

    # 2. Start the scheduler in a separate daemon thread
    t = threading.Thread(target=run_scheduler_background, daemon=True)
    t.start()
    print("✅ [System] Background monitoring started.")
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
    
    if agent_name in ["content_creator", "inventory_analyst", "strategic_analyst", "integrity_manager", "market_research", "inventory_ops"]:
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
        elif agent_name == "inventory_ops":
            from ai_agents.inventory_ops import InventoryOpsAgent
            agent = InventoryOpsAgent()
        elif agent_name == "market_research":
            from ai_agents.market_research import MarketResearchAgent
            agent = MarketResearchAgent()
            
        threading.Thread(target=agent.run).start()
        return {"status": "started", "agent": agent_name}
        
    return {"status": "error", "message": "Unknown agent"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.debug"}

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

@app.post("/debug/trigger-content")
async def trigger_content(background_tasks: BackgroundTasks):
    """
    Manually trigger content generation (for testing).
    """
    from scheduler import job_create_content
    background_tasks.add_task(job_create_content)
    return {"status": "triggered", "message": "Content generation started in background"}

@app.get("/debug/scheduler")
async def get_scheduler_status(username: str = Depends(get_current_username)):
    """
    Returns the list of pending jobs in the scheduler.
    """
    try:
        jobs = []
        for job in schedule.jobs:
            jobs.append({
                "job": getattr(job.job_func, "__name__", str(job.job_func)),
                "next_run": str(job.next_run),
                "last_run": str(job.last_run),
                "interval": str(job.interval),
                "unit": str(job.unit)
            })
        return {"jobs": jobs}
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}

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

@app.get("/api/events")
async def event_stream(request: Request):
    """
    SSE endpoint for real-time progress updates.
    """
    async def stream():
        # Optional: Send initial connected message
        yield f"data: {json.dumps({'type': 'system', 'message': 'SSE Connected'})}\n\n"
        
        async for event in event_manager.subscribe():
            # Check if client is still connected
            if await request.is_disconnected():
                break
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")

@app.get("/api/sync-reports")
async def manual_sync_reports(username: str = Depends(get_current_username)):
    """Manually trigger report sync from files to DB."""
    try:
        sync_reports_to_db()
        return {"status": "success", "message": "Reports synced successfully from folders."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

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

@app.get("/api/agents/status")
async def get_agents_status(username: str = Depends(get_current_username)):
    """Return the most recent execution logs for all AI agents."""
    try:
        from ai_agents.overseer import OverseerAgent
        overseer = OverseerAgent()
        logs = overseer._get_agent_status(limit=50)
        
        # Group by agent, keeping only the most recent one for each
        latest_status = {}
        for row in logs:
            name = row['agent_name']
            if name not in latest_status:
                latest_status[name] = row
                
        return {"status": "success", "agents": latest_status}
    except Exception as e:
        return {"status": "error", "message": str(e)}

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
        
        # 2. Business Stats (Pivoted to Haravan)
        def fetch_business_stats():
            from haravan_client import HaravanClient
            hrv = HaravanClient()
            
            # Month Summary
            sales_month = hrv.get_sales_report(period="month")
            
            # BI Data: Daily Revenue (Last 30 days)
            daily_rev = hrv.get_daily_revenue(period="30days")
            
            # BI Data: Inventory ABC Distribution (Approximate via Analyst logic)
            # To keep it fast, we could cache this or use a lightweight version
            from ai_agents.inventory_analyst import InventoryAnalystAgent
            analyst = InventoryAnalystAgent()
            # Note: analyze_stock is expensive, maybe we should return a simplified version
            # or use the cached version if available.
            inventory_report = analyst.analyze_stock()
            
            return {
                "sales_total": sales_month.get("total_sales", 0),
                "orders_count": sales_month.get("total_orders", 0),
                "new_customers": sales_month.get("total_customers", 0),
                "bi": {
                    "daily_revenue": daily_rev,
                    "inventory": {
                        "a": len(inventory_report.get("group_a", [])),
                        "b": len(inventory_report.get("group_b", [])),
                        "c": len(inventory_report.get("group_c", []))
                    }
                }
            }
            
        business_stats = await asyncio.to_thread(fetch_business_stats)
        
        return {
            "system": system_health,
            "business": business_stats
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
            elif name == "bi_analyst":
                from ai_agents.bi_analyst import BIAnalystAgent
                agent = BIAnalystAgent()
                result = agent.run_daily_summary()
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
            elif name == "auto_debug":
                from ai_agents.auto_debug import AutoDebugAgent
                agent = AutoDebugAgent()
                run_result = agent.run()
                result = run_result.get('output', 'AutoDebug scan complete.')
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
        now_hanoi = get_now_hanoi()
        c.execute("INSERT INTO reports (agent_name, report_type, content, created_at) VALUES (?, ?, ?, ?)",
                  (f"{agent_name}_{now_hanoi.strftime('%Y%m%d%H%M')}.md", "markdown", content, now_hanoi))
        conn.commit()
        conn.close()
        
        # Send Telegram Notification
        try:
            from ai_agents.telegram_client import send_telegram_message
            import html
            # Escape HTML for telegram
            clean_snippet = html.escape(content[:400]) + ("..." if len(content) > 400 else "")
            
            message = f"✅ <b>Report Generated: {agent_name}</b>\n\n{clean_snippet}\n\n<a href='https://mecobooks-ai-agent.onrender.com/verify'>Xem trên Dashboard</a>"
            send_telegram_message(message)
        except Exception as e:
            print(f"Failed to send Telegram notification: {e}")


    return {"status": "success", "agent": agent_name, "output": content}

@app.post("/api/generate-video/{report_id}")
async def generate_video_api(report_id: int, username: str = Depends(get_current_username)):
    """
    Experimental endpoint to generate a video from a stored marketing report.
    """
    import asyncio
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT content FROM reports WHERE id = ?", (report_id,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Report not found")
        
    content = row[0]
    
    # Simple Parsing Logic
    import re
    # Extract clean title: Marketing Content: Name -> Name
    title_match = re.search(r"Marketing Content: (.*?)(?:\n|\()", content)
    script_match = re.search(r"### 🎬 Video Script \(Shorts/Reels\)\n\n([\s\S]*?)\n\n", content)
    
    if not title_match or not script_match:
        # Fallback if specific headers not found
        title = "Marketing Video"
        script = content[:500] # Use snippet as fallback
    else:
        title = title_match.group(1).strip()
        script = script_match.group(1).strip()
    
    # Cleanup script: Remove line references like (00:00 - 00:05)
    script_clean = re.sub(r"\(\d{2}:\d{2} - \d{2}:\d{2}\)", "", script).strip()
    
    # Fetch Product Image URL from WooCommerce (Search by title)
    from woocommerce_client import WooCommerceClient
    woo = WooCommerceClient()
    # Search with a cleaner title to improve hits and speed
    search_query = title.split("(")[0].strip()
    print(f"🔍 Searching WooCommerce for: {search_query} (Original: {title})")
    products = woo.search_products(search_query, limit=1)
    
    image_url = "https://placehold.co/1080x1920?text=MecoBooks+AI"
    if products:
        print(f"✅ Found product: {products[0]['name']}")
        image_url = products[0]['image']
    else:
        print(f"⚠️ No product found for '{search_query}'. Using fallback image.")
    
    # Run Video Generation
    try:
        from video_processor import VideoProcessor
        vp = VideoProcessor()
        
        video_data = {
            "title": title,
            "script": script_clean,
            "image_url": image_url,
            "id": str(report_id)
        }
        
        # Run in thread to avoid blocking FastAPI
        print(f"🎞️ Starting video processing for record {report_id}...")
        output_path = await asyncio.to_thread(vp.generate_video, video_data)
        
        if output_path and os.path.exists(output_path):
            print(f"✅ Video created successfully: {output_path}")
            # Dynamic URL based on host
            video_url = f"/static/videos/{os.path.basename(output_path)}"
            
            # Notify via Telegram
            try:
                from ai_agents.telegram_client import send_telegram_message
                message = f"🎬 <b>Video Đã Sẵn Sàng!</b>\n\nNội dung: {title}\n\n<a href='https://mecobooks-ai-agent.onrender.com{video_url}'>Xem và Tải Video</a>"
                send_telegram_message(message)
            except Exception as te:
                print(f"Telegram Video Error: {te}")
                
            return {"status": "success", "video_url": video_url}
        else:
            print(f"❌ Video generation failed for {report_id}")
            return {"status": "error", "message": "Video generation failed. Please check server logs for details."}
            
    except Exception as e:
        print(f"Video API Error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

@app.get("/api/compare-price")
async def compare_price(q: str, username: str = Depends(get_current_username)):
    """Scouts multiple platforms for book prices."""
    if not q:
        return {"results": []}
    def run_scout():
        from ai_agents.price_scout import PriceScoutAgent
        scout = PriceScoutAgent()
        return scout.compare(q)
    results = await asyncio.to_thread(run_scout)
    return {"query": q, "results": results}

@app.get("/api/price-strategy/suggest")
async def price_strategy_suggest(q: str, category: str = "default", username: str = Depends(get_current_username)):
    """Returns a Tier-1, Tier-2 and scarcity pricing suggestion for a given book title."""
    if not q:
        return {"error": "Missing book title."}
    def run_suggest():
        from ai_agents.pricing_strategy import PricingStrategyAgent
        agent = PricingStrategyAgent()
        return agent.suggest_prices(q, category=category)
    result = await asyncio.to_thread(run_suggest)
    return result

@app.post("/api/price-strategy/apply-markdowns")
async def apply_price_markdowns(dry_run: bool = True, username: str = Depends(get_current_username)):
    """
    Scans inventory for products unsold > 30 days and applies Tier-2 pricing.
    Set dry_run=False to commit changes to Haravan.
    """
    def run_markdown():
        from ai_agents.pricing_strategy import PricingStrategyAgent
        agent = PricingStrategyAgent()
        return agent.apply_markdown(dry_run=dry_run)
    result = await asyncio.to_thread(run_markdown)
    return result

@app.get("/api/price-strategy/history")
async def price_strategy_history(limit: int = 50, username: str = Depends(get_current_username)):
    """Returns the history of all pricing tier transitions from the local SQLite DB."""
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(__file__), "pricing_history.db")
    if not os.path.exists(db_path):
        return {"history": [], "message": "Chưa có lịch sử thay đổi giá nào."}
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM pricing_history ORDER BY transitioned_at DESC LIMIT ?",
                (limit,)
            ).fetchall()
        return {"history": [dict(r) for r in rows]}
    except Exception as e:
        return {"history": [], "error": str(e)}

@app.get("/api/price-strategy/bundle-suggestions")
async def price_strategy_bundle_suggestions(username: str = Depends(get_current_username)):
    """Finds bundling opportunities for Tier 2 products."""
    def run_scan():
        from ai_agents.pricing_strategy import PricingStrategyAgent
        agent = PricingStrategyAgent()
        return agent.find_bundle_opportunities()
    result = await asyncio.to_thread(run_scan)
    return {"suggestions": result}

@app.post("/api/price-strategy/create-bundle")
async def price_strategy_create_bundle(item_ids: list, title: str, price: int, username: str = Depends(get_current_username)):
    """Creates a bundle product on Haravan."""
    def run_create():
        from ai_agents.pricing_strategy import PricingStrategyAgent
        agent = PricingStrategyAgent()
        return agent.create_bundle(item_ids, title, price)
    result = await asyncio.to_thread(run_create)
    return result

@app.post("/api/price-strategy/sync-bundles")
async def price_strategy_sync_bundles(username: str = Depends(get_current_username)):
    """Triggers a manual sync of bundle inventory."""
    def run_sync():
        from ai_agents.pricing_strategy import PricingStrategyAgent
        agent = PricingStrategyAgent()
        return agent.sync_bundle_inventory()
    result = await asyncio.to_thread(run_sync)
    return result

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

@app.post("/api/run-inventory-sync")
async def run_inventory_sync(background_tasks: BackgroundTasks, username: str = Depends(get_current_username)):
    """
    Triggers the Inventory Ops Agent in background.
    """
    try:
        from ai_agents.inventory_ops import InventoryOpsAgent
        agent = InventoryOpsAgent()
        background_tasks.add_task(agent.run)
        return {"status": "success", "message": "Tiến trình đồng bộ kho hàng đã bắt đầu chạy ngầm. Kết quả sẽ được gửi qua Telegram và lưu vào báo cáo."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port)
