import requests
import time

BOT_TOKEN = "8460049803:AAGxKOO3buc-vX8mk-uTcShlN52gwgKIaqA"

def get_chat_id():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    print(f"Checking for updates on {url}...")
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if not data.get("ok"):
            print("Error:", data)
            return

        results = data.get("result", [])
        if not results:
            print("No new messages found. Please send '/start' or any message to your bot @Mecobooksbot")
            return

        # Get the chat ID from the latest message
        latest_update = results[-1]
        chat = latest_update.get("message", {}).get("chat", {})
        chat_id = chat.get("id")
        username = chat.get("username")
        type = chat.get("type")
        
        print(f"\n✅ FOUND CHAT ID: {chat_id}")
        print(f"User/Group: {username} ({type})")
        print("\nPlease save this Chat ID for your config.")
        return chat_id

    except Exception as e:
        print(f"Error fetching updates: {e}")

if __name__ == "__main__":
    get_chat_id()
