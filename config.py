# Haravan API Configuration
# Replace with your actual details

HARAVAN_SHOP_URL = "https://tiem-sach-anh-tuan.myharavan.com/"
HARAVAN_ACCESS_TOKEN = "760F4B6BBE2F5506FAAB3F19120278F3298034D94100D0839CE816479752F06B"

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Gemini API Configuration
# NO HARDCODED KEYS ALLOWED. All keys must be set in .env or system environment.

def get_required_key(env_name):
    key = os.environ.get(env_name, "").strip()
    if not key:
        print(f"❌ Error: {env_name} is missing or empty. System limited.")
        return ""
    if len(key) < 39:
        print(f"⚠️ Warning: {env_name} looks invalid/truncated ({len(key)} chars).")
        return ""
    return key

GEMINI_API_KEY = get_required_key("GEMINI_API_KEY")
GOOGLE_TTS_API_KEY = get_required_key("GOOGLE_TTS_API_KEY")

# Fallback to Gemini Key for TTS if TTS key is missing
if not GOOGLE_TTS_API_KEY and GEMINI_API_KEY:
    GOOGLE_TTS_API_KEY = GEMINI_API_KEY


# Video Generation Config
OUTPUT_VIDEO_DIR = "output_videos"
TEMP_IMAGE_DIR = "temp_images"

# WooCommerce Configuration
WOO_URL = os.environ.get("WOO_URL", "https://mecobooks.com")
WOO_CONSUMER_KEY = os.environ.get("WOO_CONSUMER_KEY", "ck_fd2ff641bb7d799f65a0d9877f5e4fd125fac599")
WOO_CONSUMER_SECRET = os.environ.get("WOO_CONSUMER_SECRET", "cs_9c22398f5238bb57e01a7e83ebc7f597aa2a706c")

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8460049803:AAGxKOO3buc-vX8mk-uTcShlN52gwgKIaqA")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "8425705625")

# Timezone Configuration (Asia/Ho_Chi_Minh - UTC+7)
from datetime import datetime, timezone, timedelta
HANOI_TZ = timezone(timedelta(hours=7))

def get_now_hanoi():
    """Returns the current datetime in Hanoi timezone."""
    return datetime.now(HANOI_TZ)
