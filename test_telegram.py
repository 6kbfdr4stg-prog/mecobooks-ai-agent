import requests
import os
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def test_send():
    print(f"Token: {TELEGRAM_BOT_TOKEN[:10]}...")
    print(f"Chat ID: {TELEGRAM_CHAT_ID}")
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": "🚀 **Mecobooks AI Agent**\n\nKiểm tra lại kết nối...",
        "parse_mode": "HTML"
    }

    response = requests.post(url, json=payload, timeout=10)
    print("Response Status:", response.status_code)
    print("Response Body:", response.json())

if __name__ == "__main__":
    test_send()

