import os
from dotenv import load_dotenv

# Load environment variables from .env file for local development
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Declare global variables
HARAVAN_SHOP_URL = ""
HARAVAN_ACCESS_TOKEN = ""
GEMINI_API_KEY = ""
GOOGLE_TTS_API_KEY = ""
WOO_URL = ""
WOO_CONSUMER_KEY = ""
WOO_CONSUMER_SECRET = ""
TELEGRAM_BOT_TOKEN = ""
TELEGRAM_CHAT_ID = ""

def reload_config():
    """Reads environment variables from .env/secrets.env and updates globals."""
    global HARAVAN_SHOP_URL, HARAVAN_ACCESS_TOKEN, GEMINI_API_KEY, GOOGLE_TTS_API_KEY
    global WOO_URL, WOO_CONSUMER_KEY, WOO_CONSUMER_SECRET, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
    
    # Try .env first, then fallback to secrets.env (to bypass MacOS permissions)
    env_paths = [os.path.join(BASE_DIR, ".env"), os.path.join(BASE_DIR, "secrets.env")]
    for env_path in env_paths:
        if os.path.exists(env_path):
            load_dotenv(env_path, override=True)
        else:
            try: load_dotenv(env_path, override=True)
            except: pass

    HARAVAN_SHOP_URL = os.environ.get("HARAVAN_SHOP_URL", "https://tiem-sach-anh-tuan.myharavan.com/")
    HARAVAN_ACCESS_TOKEN = os.environ.get("HARAVAN_ACCESS_TOKEN", "")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
    GOOGLE_TTS_API_KEY = os.environ.get("GOOGLE_TTS_API_KEY", "").strip() or GEMINI_API_KEY
    WOO_URL = os.environ.get("WOO_URL", "https://mecobooks.com")
    WOO_CONSUMER_KEY = os.environ.get("WOO_CONSUMER_KEY", "")
    WOO_CONSUMER_SECRET = os.environ.get("WOO_CONSUMER_SECRET", "")
    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# Initial load
reload_config()


# Timezone Configuration (Asia/Ho_Chi_Minh - UTC+7)
from datetime import datetime, timezone, timedelta
HANOI_TZ = timezone(timedelta(hours=7))

def get_now_hanoi():
    """Returns the current datetime in Hanoi timezone."""
    return datetime.now(HANOI_TZ)
