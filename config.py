# Haravan API Configuration
# Replace with your actual details

HARAVAN_SHOP_URL = "https://tiem-sach-anh-tuan.myharavan.com/"
HARAVAN_ACCESS_TOKEN = "760F4B6BBE2F5506FAAB3F19120278F3298034D94100D0839CE816479752F06B"

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Gemini API Configuration
# Fallback hardcoded values (Known Good)
FALLBACK_GEMINI_KEY = "AIzaSyCdDjbxja5Kp9107JNyd8x8xBYKWnPp2nU"
FALLBACK_TTS_KEY = "AIzaSyBsXsKTO_g4tUVmKxNW1JPlOpLNGxGBIqE"

def get_valid_key(env_name, fallback):
    key = os.environ.get(env_name, "").strip()
    if len(key) < 39:
        if key:
            print(f"⚠️ Warning: {env_name} looks truncated ({len(key)} chars). Using internal fallback.")
        return fallback
    return key

GEMINI_API_KEY = get_valid_key("GEMINI_API_KEY", FALLBACK_GEMINI_KEY)
GOOGLE_TTS_API_KEY = get_valid_key("GOOGLE_TTS_API_KEY", GEMINI_API_KEY)
# Double check: if GOOGLE_TTS_API_KEY is still too short (e.g if GEMINI_API_KEY was the truncated one), 
# use the specific TTS fallback
if len(GOOGLE_TTS_API_KEY) < 39:
    GOOGLE_TTS_API_KEY = FALLBACK_TTS_KEY


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
