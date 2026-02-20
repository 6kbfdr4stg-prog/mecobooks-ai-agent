import os
from dotenv import load_dotenv

# Haravan API Configuration
# Replace with your actual details

HARAVAN_SHOP_URL = os.environ.get("HARAVAN_SHOP_URL", "https://tiem-sach-anh-tuan.myharavan.com/")
HARAVAN_ACCESS_TOKEN = os.environ.get("HARAVAN_ACCESS_TOKEN", "")

# --- (Previous logic for Gemini already updated) ---

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
