# Haravan API Configuration
# Replace with your actual details

HARAVAN_SHOP_URL = "https://tiem-sach-anh-tuan.myharavan.com/"
HARAVAN_ACCESS_TOKEN = "760F4B6BBE2F5506FAAB3F19120278F3298034D94100D0839CE816479752F06B"

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Gemini API Configuration
# API Key is now loaded from Environment Variables for security
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")


# Video Generation Config
OUTPUT_VIDEO_DIR = "output_videos"
TEMP_IMAGE_DIR = "temp_images"

# WooCommerce Configuration
WOO_URL = os.environ.get("WOO_URL", "https://mecobooks.com")
WOO_CONSUMER_KEY = os.environ.get("WOO_CONSUMER_KEY")
WOO_CONSUMER_SECRET = os.environ.get("WOO_CONSUMER_SECRET")

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8460049803:AAGxKOO3buc-vX8mk-uTcShlN52gwgKIaqA")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "8425705625")
