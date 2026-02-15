from fastapi import FastAPI, HTTPException, Request, Response, Form, File, UploadFile
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

# Facebook Config
FB_VERIFY_TOKEN = os.environ.get("FB_VERIFY_TOKEN", "my_secure_verify_token")
FB_PAGE_ACCESS_TOKEN = os.environ.get("FB_PAGE_ACCESS_TOKEN")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Haravan AI Chatbot is running"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(message: str = Form(...), file: UploadFile = File(None)):
    if not bot:
        raise HTTPException(status_code=500, detail="Chatbot not initialized properly")
    
    try:
        image_data = None
        if file:
            print(f"Received file: {file.filename}")
            image_data = await file.read()
            
        response_text = bot.process_message(message, image_data=image_data)
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
