from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chatbot import Chatbot
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

# Initialize Chatbot
try:
    bot = Chatbot()
except Exception as e:
    print(f"Failed to initialize chatbot: {e}")
    bot = None

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

# Facebook Config
FB_VERIFY_TOKEN = os.environ.get("FB_VERIFY_TOKEN", "my_secure_verify_token")
FB_PAGE_ACCESS_TOKEN = os.environ.get("FB_PAGE_ACCESS_TOKEN")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Haravan AI Chatbot is running"}

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    if not bot:
        raise HTTPException(status_code=500, detail="Chatbot not initialized properly")
    
    try:
        response_text = bot.process_message(request.message)
        return {"response": response_text}
    except Exception as e:
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
            return int(challenge)
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
                    
                    if message_text:
                        # Process message with Chatbot
                        response_text = "Xin lỗi, chatbot chưa sẵn sàng."
                        if bot:
                            try:
                                response_text = bot.process_message(message_text)
                            except Exception as e:
                                print(f"Bot Error: {e}")
                                response_text = "Có lỗi xảy ra khi xử lý tin nhắn."

                        # Send response back to Facebook
                        send_fb_message(sender_id, response_text)
        
        return Response(content="EVENT_RECEIVED", status_code=200)
    else:
        raise HTTPException(status_code=404, detail="Not a page event")

def send_fb_message(recipient_id, text):
    """
    Send text message back to Facebook User.
    """
    if not FB_PAGE_ACCESS_TOKEN:
        print("Missing FB_PAGE_ACCESS_TOKEN")
        return

    url = f"https://graph.facebook.com/v22.0/me/messages?access_token={FB_PAGE_ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    
    try:
        r = requests.post(url, headers=headers, json=payload)
        if r.status_code != 200:
            print(f"Failed to send message: {r.text}")
    except Exception as e:
        print(f"Error sending message: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
