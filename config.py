import os
from dotenv import load_dotenv

# Haravan API Configuration
# Replace with your actual details

HARAVAN_SHOP_URL = os.environ.get("HARAVAN_SHOP_URL", "https://tiem-sach-anh-tuan.myharavan.com/")
HARAVAN_ACCESS_TOKEN = os.environ.get("HARAVAN_ACCESS_TOKEN", "")

# Gemini API Configuration
def get_required_key(env_name):
    key = os.environ.get(env_name, "").strip()
    if not key:
        return ""
    return key

GEMINI_API_KEY = get_required_key("GEMINI_API_KEY")
GOOGLE_TTS_API_KEY = get_required_key("GOOGLE_TTS_API_KEY")

# Fallback to Gemini Key for TTS if TTS key is missing
if not GOOGLE_TTS_API_KEY and GEMINI_API_KEY:
    GOOGLE_TTS_API_KEY = GEMINI_API_KEY

# WooCommerce Configuration
WOO_URL = os.environ.get("WOO_URL", "https://mecobooks.com")
WOO_CONSUMER_KEY = os.environ.get("WOO_CONSUMER_KEY", "")
WOO_CONSUMER_SECRET = os.environ.get("WOO_CONSUMER_SECRET", "")

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# Timezone Configuration (Asia/Ho_Chi_Minh - UTC+7)
from datetime import datetime, timezone, timedelta
HANOI_TZ = timezone(timedelta(hours=7))

def get_now_hanoi():
    """Returns the current datetime in Hanoi timezone."""
    return datetime.now(HANOI_TZ)
