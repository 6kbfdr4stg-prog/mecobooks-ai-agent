# Haravan API Configuration
# Replace with your actual details

HARAVAN_SHOP_URL = "https://tiem-sach-anh-tuan.myharavan.com/"
HARAVAN_ACCESS_TOKEN = "760F4B6BBE2F5506FAAB3F19120278F3298034D94100D0839CE816479752F06B"

import os

# Gemini API Configuration
# API Key is now loaded from Environment Variables for security
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")


# Video Generation Config
OUTPUT_VIDEO_DIR = "output_videos"
TEMP_IMAGE_DIR = "temp_images"
