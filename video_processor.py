import os
import random
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
from PIL import Image, ImageFilter
import requests
from io import BytesIO
import numpy as np
import json
import base64
import hashlib
from config import GOOGLE_TTS_API_KEY

# Configuration
VIDEO_W, VIDEO_H = 1080, 1920
FPS = 24
STATIC_VIDEO_DIR = "static/videos"

os.makedirs(STATIC_VIDEO_DIR, exist_ok=True)

class VideoProcessor:
    def __init__(self):
        pass

    def _download_image(self, url):
        """Downloads image or returns a fallback solid color image if failed"""
        try:
            # Try to fix MoviePy / ImageMagick issues for Linux if they exist
            # Note: We don't use TextClip, so this is mostly defensive
            try:
                from moviepy.config import change_settings
                if os.name != 'nt': # Linux/Mac
                    change_settings({"IMAGEMAGICK_BINARY": "convert"})
            except Exception as e:                pass

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            # If it's the placeholder URL, let's just create it ourselves to be safe and fast
            if "placehold.co" in url:
                 print("🛠️ Using internal fallback image generator")
                 return self._create_solid_image("MecoBooks AI")

            response = requests.get(url, headers=headers, timeout=20)
            if response.status_code == 200:
                print(f"✅ Image downloaded successfully: {url}")
                return Image.open(BytesIO(response.content)).convert("RGB")
            else:
                print(f"❌ Failed to download image. Status code: {response.status_code}")
        except Exception as e:
            print(f"❌ Error downloading image: {e}")
        
        # FINAL FALLBACK: Create a nice gradient or solid image
        print("⚠️ Using final fallback image")
        return self._create_solid_image("MecoBooks AI")

    def _create_solid_image(self, text="MecoBooks"):
        """Creates a simple 1080x1920 image as fallback"""
        img = Image.new('RGB', (VIDEO_W, VIDEO_H), color=(30, 30, 30))
        # Optional: Add some noise or a simple shape so it's not pure black
        return img

    def _create_portrait_image(self, pil_image):
        """Creates a 9:16 image with blurred background"""
        bg = pil_image.copy().resize((VIDEO_W, VIDEO_H)).filter(ImageFilter.GaussianBlur(radius=30))
        
        # Resize foreground to fit width or height
        iw, ih = pil_image.size
        # Try to fit width mostly, but keep within bounds
        scale = min(VIDEO_W / iw, VIDEO_H / ih) * 0.85 # 85% fill
        new_w, new_h = int(iw * scale), int(ih * scale)
        fg = pil_image.resize((new_w, new_h), Image.LANCZOS)
        
        # Center paste
        x = (VIDEO_W - new_w) // 2
        y = (VIDEO_H - new_h) // 2
        bg.paste(fg, (x, y))
        
        # Save to temp file
        temp_path = f"temp_img_{random.randint(1000,9999)}.jpg"
        bg.save(temp_path)
        return temp_path

    def _generate_tts(self, text, lang='vi-VN'):
        """Generates TTS audio using Google Cloud TTS REST API"""
        if not GOOGLE_TTS_API_KEY:
            print("⚠️ Missing GOOGLE_TTS_API_KEY. Video will have no audio.")
            return None

        url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_TTS_API_KEY}"
        
        # Voice Config (Using a high-quality neural voice as default)
        voice_name = "vi-VN-Neural2-A" 
        
        payload = {
            "input": {"text": text},
            "voice": {"languageCode": lang, "name": voice_name},
            "audioConfig": {
                "audioEncoding": "MP3",
                "speakingRate": 1.0,
                "pitch": 0.0
            }
        }

        try:
            # Debug: Log masked key
            masked_key = GOOGLE_TTS_API_KEY[:5] + "..." + GOOGLE_TTS_API_KEY[-4:] if GOOGLE_TTS_API_KEY else "None"
            print(f"📡 Calling Google TTS API (Key: {masked_key})")
            
            response = requests.post(url, json=payload, timeout=20)
            
            if response.status_code != 200:
                print(f"❌ Google TTS API Error {response.status_code}: {response.text}")
                return None
                
            audio_content = response.json().get("audioContent")
            if not audio_content:
                print("❌ No audio content returned from Google TTS")
                return None
                
            temp_audio = f"temp_audio_{random.randint(1000,9999)}.mp3"
            with open(temp_audio, "wb") as f:
                f.write(base64.b64decode(audio_content))
                
            print(f"✅ TTS generated successfully using Google API")
            return temp_audio
            
        except Exception as e:
            print(f"TTS Exception: {e}")
            return None

    def _ken_burns_zoom(self, clip, zoom_ratio=1.1):
        """Applies a slow zoom effect"""
        def effect(get_frame, t):
            img = Image.fromarray(get_frame(t))
            base_size = img.size
            
            # Zoom Factor over time
            progress = t / clip.duration
            current_zoom = 1 + (zoom_ratio - 1) * progress
            
            # Resize
            new_size = (int(base_size[0] * current_zoom), int(base_size[1] * current_zoom))
            img_zoomed = img.resize(new_size, Image.LANCZOS)
            
            # Center Crop
            x = (new_size[0] - base_size[0]) // 2
            y = (new_size[1] - base_size[1]) // 2
            img_cropped = img_zoomed.crop((x, y, x + base_size[0], y + base_size[1]))
            
            return np.array(img_cropped)
        
        # MoviePy's resize is simpler and faster than custom per-frame
        # Simple Zoom: resize to 1.1x over duration, always keep centered
        # Using built-in resize with lambda
        return clip.resize(lambda t: 1 + 0.05 * t) # Simple linear zoom

    def generate_video(self, product_data):
        """
        Main function to create video.
        product_data: {'title': str, 'image_url': str, 'script': str, 'id': str}
        """
        print(f"🎬 Creating video for: {product_data.get('title')}")
        
        # 1. Image
        pil_img = self._download_image(product_data.get('image_url'))
        if not pil_img:
            return None
        
        img_path = self._create_portrait_image(pil_img)
        
        # 2. Audio
        audio_path = self._generate_tts(product_data.get('script'))
        if not audio_path:
            return None
            
        # 3. Assemble
        try:
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration + 0.5 # Add small padding
            
            # Video Clip
            video_clip = ImageClip(img_path).set_duration(duration)
            
            # Apply Zoom (Simple implementation to avoid complex dependencies)
            # We will interpret "Ken Burns" as a simple resize zoom here
            # video_clip = video_clip.resize(lambda t : 1 + 0.02*t)  # Zoom in 2% per sec
            # Note: resize is CPU intensive. Let's stick to static first for speed on Render, 
            # or very simple zoom.
             
            # Center on 1080x1920 (it already is, but safety check)
            video_clip = video_clip.set_position("center")
            
            # Combine
            final_clip = video_clip.set_audio(audio_clip)
            final_clip.fps = FPS
            
            # Output Path
            output_filename = f"video_{product_data.get('id')}.mp4"
            output_path = os.path.join(STATIC_VIDEO_DIR, output_filename)
            
            final_clip.write_videofile(
                output_path, 
                codec="libx264", 
                audio_codec="aac", 
                threads=1, # Reduce to 1 thread for memory stability on Render free tier
                preset="ultrafast",
                logger="bar" 
            )
            
            # Cleanup Temps
            os.remove(img_path)
            os.remove(audio_path)
            
            return output_path
            
        except Exception as e:
            print(f"Video Generation Error: {e}")
            import traceback
            traceback.print_exc()
            return None
            
if __name__ == "__main__":
    # Test
    vp = VideoProcessor()
    data = {
        "title": "Test Book",
        "script": "Xin chào, đây là video thử nghiệm cho cuốn sách Nhà Giả Kim. Cuốn sách bán chạy nhất mọi thời đại.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/The_Alchemist_by_Paulo_Coelho_book_cover.jpg/330px-The_Alchemist_by_Paulo_Coelho_book_cover.jpg",
        "id": "test_01"
    }
    vp.generate_video(data)
