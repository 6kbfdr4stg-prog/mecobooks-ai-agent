# ===========================================
# Google Sheet -> Google TTS (Cloud Text-to-Speech via REST) -> Video (NO SUBTITLE)
# -> Google Drive (MyDrive/VbeeVideos/run_YYYYmmdd_HHMMSS) + ZIP
# + Skip dòng đã DONE, cache TTS/ảnh, retry, batch update
# + Chia nhỏ câu + Ken Burns mượt theo từng câu
# + Xuất khung dọc 9:16 (portrait)
# + Ghi LINK DRIVE CÔNG KHAI vào cột output_file
# ===========================================

# --- CÀI THƯ VIỆN (thêm google-api-python-client) ---
!apt-get update && apt-get install -y imagemagick libmagick++-dev
!sed -i '/<policy domain="path" rights="none" pattern="@\*"/d' /etc/ImageMagick-6/policy.xml || true
!pip -q install gspread pandas moviepy==1.0.3 pillow requests tqdm python-slugify google-auth google-api-python-client openai-whisper ffmpeg-python google-auth-oauthlib google-auth-httplib2

import os, re, io, time, shutil, requests, warnings, hashlib, random, gc, sys, json, base64
import torch
from pathlib import Path
from typing import List, Dict, Tuple
import pandas as pd
from PIL import Image, ImageFilter, UnidentifiedImageError
from tqdm import tqdm
from slugify import slugify
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry





from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips, TextClip, VideoFileClip, CompositeAudioClip
)

warnings.filterwarnings("ignore")

# ================== CONFIG ==================
# ---- Môi trường (Colab vs Local) ----
try:
    import google.colab
    IN_COLAB = True
    print("✨ Running in Google Colab")
except:
    IN_COLAB = False
    print("🖥️ Running Locally")

# Create a project dir
if IN_COLAB:
    # Mount Drive
    from google.colab import drive
    drive.mount('/content/drive')
    PROJECT_DIR = "/content/drive/MyDrive/VbeeVideos"
    RUN_DIR = os.path.join(PROJECT_DIR, f"run_{time.strftime('%Y%m%d_%H%M%S')}")
else:
    PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
    RUN_DIR = os.path.join(PROJECT_DIR, "output", f"run_{time.strftime('%Y%m%d_%H%M%S')}")

Path(PROJECT_DIR).mkdir(parents=True, exist_ok=True)

# ---- Google Sheet (MASTER DB) ----
SHEET_ID   = "1rdrbMPNJiybI4k7au8gW8bmfoPi_ybrjjwaf0BAuNGk"   # <-- Master Sheet ID (Thay đổi nếu cần)
SHEET_NAME = "San pham (Master)"                            # <-- Tên sheet MASTER

# ---- Cột dữ liệu (Mapping theo Master) ----
COL_SKU   = "SKU"
COL_TITLE = "Tên sách"
COL_DESC  = "Mô tả dài"          # Hoặc "Mô tả ngắn"
COL_STOCK = "Tồn kho"            # Chỉ làm video nếu tồn kho > 0
IMAGE_COLS = [f"Image_{i}" for i in range(1, 11)]

# ---- Trạng thái & Output ----
STATUS_COL = "Video_Status"      # PENDING -> DONE
OUTPUT_COL = "Video_URL"         # Link YouTube (Final - do Apps Script ghi)
DRIVE_COL  = "Video_Drive"       # Link Google Drive (Output của script này)

# ---- GOOGLE TTS (dùng API key REST) ----
# Bạn cần đặt ENV: export GOOGLE_TTS_API_KEY="..."
# Nếu không có ENV, script sẽ không thể tạo giọng nói.
GOOGLE_TTS_API_KEY = os.environ.get("GOOGLE_TTS_API_KEY", "").strip()
GOOGLE_TTS_ENDPOINT = "https://texttospeech.googleapis.com/v1/text:synthesize"

# Giữ các biến Vbee để không phải đổi pipeline; ánh xạ sang Google TTS
# Voice Nâng cao: vi-VN-Neural2-A / vi-VN-Neural2-D (Nữ/Nam)
# Voice Studio (Cực xịn): vi-VN-Chirp3-HD-Achernar (như ảnh)
VBEE_VOICE      = "vi-VN-Chirp3-HD-Achernar"  # Mặc định dùng Neural2 (Nâng cao). Nếu muốn Studio hãy điền vào cột voice_code
VBEE_AUDIO_TYPE = "mp3"             # "mp3" hoặc "wav" (LINEAR16)
VBEE_BITRATE    = 128                # KHÔNG dùng cho Google REST, giữ cho tương thích
VBEE_SPEED      = "1.0"             # speaking_rate (chuỗi)
VBEE_EXTRA: Dict = {}                # KHÔNG dùng, giữ chỗ

# ---- Thông số video (9:16 portrait) ----
VIDEO_W, VIDEO_H = 1080, 1920   # <— 9:16
FPS = 30
FADE_IN, FADE_OUT = 0.3, 0.3
DEFAULT_PER_IMAGE = 3.0
MAX_IMG_PER_ROW = 10
IMG_DL_WORKERS = 5

# ---- Timeout / Retry ----
HTTP_TIMEOUT = 30

# ---- Ken Burns ----
KB_MIN_ZOOM = 1.03   # 3%
KB_MAX_ZOOM = 1.08   # 8%

# ---- Khác ----
RANDOM_SEED_BASE = 20251006  # để tái hiện hiệu ứng nhất quán theo lần chạy

# ---- Config Nhạc nền ----
MUSIC_DRIVE_FOLDER = "1rVo_R7PLB897LzsqFmnRGtHWIRZi_aK3"  # <-- Đã điền ID folder nhạc bạn gửi
MUSIC_VOLUME = 0.15           # Âm lượng nhạc nền (0.0 - 1.0)

# ---- Intro / Outro (Link Drive hoặc Link trực tiếp) ----
ENABLE_INTRO_OUTRO = True
INTRO_URL = "https://drive.google.com/file/d/1G-yfWA4vhWE-eexpdMyXusRkjljEk24i/view?usp=sharing" # <-- Dán link Intro vào đây
OUTRO_URL = "" # <-- Dán link Outro vào đây


# ---- Chế độ chạy liên tục (Continuous Mode) ----
CONTINUOUS_MODE = True        # True = Tự động lặp lại kiểm tra Sheet
CHECK_INTERVAL = 900          # 900 giây (15 phút) - Khoảng cách giữa các lần kiểm tra
CAMPAIGN_MAX_ROWS_PER_LOOP = 20 # <— Giới hạn số dòng mỗi lần quét để tránh quá tải Colab



# ---- Config Upload Drive ----
UPLOAD_MODE = True            # True = Upload mp4 lên Drive (nếu False chỉ mount)
TARGET_FOLDER_ID = "1vemvuOSt4FfW3hhVF--9oDhPLMrOXymK" # <-- Folder ID user provided
PUBLIC_LINK_DIRECT_DOWNLOAD = True # True = lấy link tải trực tiếp (webContentLink)

# ---- Fix NameError ----
BASE_DRIVE = PROJECT_DIR      # Alias cho tương thích ngược
MIRROR_WIKIPEDIA_TO_DRIVE = False
MIRROR_WRITE_BACK_TO_SHEET = False
USE_HYPERLINK_FORMULA = False
HYPERLINK_TEXT = "Xem video"

# ---- Config Upload YouTube (NEW) ----
UPLOAD_TO_YOUTUBE = False      # <-- ĐÃ TẮT: Bỏ upload YouTube theo yêu cầu
YOUTUBE_PRIVACY = "public"    # public, private, unlisted
YOUTUBE_CATEGORY_ID = "22"    # 22 = People & Blogs, 27 = Education

Path(RUN_DIR).mkdir(parents=True, exist_ok=True)

OUTPUT_DIR = RUN_DIR
# Cache always in generic project dir or local if upload mode?
# If upload mode, project dir might not be writable if not mounted properly or messy.
# Let's keep cache in PROJECT_DIR if mounted, else local.
if os.path.exists(PROJECT_DIR):
    CACHE_DIR = os.path.join(PROJECT_DIR, "_cache")
else:
    CACHE_DIR = os.path.join(RUN_DIR, "_cache")

CACHE_TTS_DIR = os.path.join(CACHE_DIR, "tts")
CACHE_IMG_DIR = os.path.join(CACHE_DIR, "images")
CACHE_IMG_PREP_DIR = os.path.join(CACHE_IMG_DIR, f"prep_{VIDEO_W}x{VIDEO_H}")
Path(CACHE_TTS_DIR).mkdir(parents=True, exist_ok=True)
Path(CACHE_IMG_DIR).mkdir(parents=True, exist_ok=True)
Path(CACHE_IMG_PREP_DIR).mkdir(parents=True, exist_ok=True)
print("📂 Nơi xuất file tạm:", OUTPUT_DIR)

# ================== AUTH GOOGLE SHEET + DRIVE + YOUTUBE ==================
def get_services(sheet_id: str, sheet_name: str):
    if not IN_COLAB:
        print("⚠️ Không ở Colab: bỏ qua kết nối Google Sheet/Drive. Dùng DataFrame rỗng.")
        return None, pd.DataFrame(), None, None # + youtube
    from google.colab import auth
    import gspread, google.auth
    from googleapiclient.discovery import build

    auth.authenticate_user()
    # Cấp scope cho cả Sheets, Drive và YouTube
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/youtube.upload",
        "https://www.googleapis.com/auth/youtube"
    ]
    creds, _ = google.auth.default(scopes=scopes)

    # Sheets
    gc_ = gspread.authorize(creds)
    sh = gc_.open_by_key(sheet_id)
    ws_ = sh.worksheet(sheet_name)
    df_ = pd.DataFrame(ws_.get_all_records())

    # Drive
    drive_service = build("drive", "v3", credentials=creds)

    # YouTube (NEW)
    youtube_service = build("youtube", "v3", credentials=creds)

    return ws_, df_, drive_service, youtube_service

ws, df, DRIVE, YOUTUBE = get_services(SHEET_ID, SHEET_NAME)
if ws is not None:
    print("✅ Số dòng đọc được:", len(df))
    print("✅ Các cột:", list(df.columns))

    # Bảo đảm 2 cột trạng thái tồn tại
    headers = list(ws.row_values(1))
    changed = False
    if STATUS_COL not in headers:
        ws.update_cell(1, len(headers)+1, STATUS_COL); headers.append(STATUS_COL); changed=True
    if OUTPUT_COL not in headers:
        ws.update_cell(1, len(headers)+1, OUTPUT_COL); headers.append(OUTPUT_COL); changed=True
    if DRIVE_COL not in headers:
        ws.update_cell(1, len(headers)+1, DRIVE_COL); headers.append(DRIVE_COL); changed=True
    if changed:
        df = pd.DataFrame(ws.get_all_records())
    col_idx = {h: i+1 for i, h in enumerate(ws.row_values(1))}
else:
    df = pd.DataFrame(columns=[COL_TITLE, COL_DESC] + IMAGE_COLS + [STATUS_COL, OUTPUT_COL, DRIVE_COL])
    col_idx = {c: i+1 for i, c in enumerate([COL_TITLE, COL_DESC] + IMAGE_COLS + [STATUS_COL, OUTPUT_COL, DRIVE_COL])}

# ================== HTTP SESSION W/ RETRY ==================
def make_session() -> requests.Session:
    s = requests.Session()
    retries = Retry(
        total=5,
        connect=5,
        read=5,
        backoff_factor=0.8,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(['GET','POST'])
    )
    adapter = HTTPAdapter(max_retries=retries, pool_connections=100, pool_maxsize=100)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    # UA chuẩn theo chính sách Wikimedia
    s.headers.update({
        "User-Agent": "GoogleTTSVideoBot/1.0 (Colab) +mailto:butlersamanthasya579@hotmail.com",
        "Accept": "image/*,application/json;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://en.wikipedia.org/"
    })
    return s

SESSION = make_session()

# ================== GOOGLE DRIVE HELPERS: PUBLIC LINK (v2) ==================
from googleapiclient.errors import HttpError

def _escape_q_val(s: str) -> str:
    return s.replace("'", "\\'")

def drive_find_id_by_path(drive, abs_path: str):
    """
    Resolve đường dẫn tuyệt đối trong MyDrive (PROJECT_DIR/...) -> fileId.
    Duyệt lần lượt từng cấp thư mục để tìm đúng parentId.
    Ưu tiên file/folder mới nhất nếu trùng tên.
    """
    if drive is None:
        return None
    if not abs_path.startswith(PROJECT_DIR):
        # Tránh lỗi nếu path có dạng /content/drive/MyDrive/...
        # Nếu path bắt đầu bằng /content/drive/MyDrive nhưng PROJECT_DIR cũng thế
        # thì OK.
        raise ValueError(f"Path {abs_path} không thuộc PROJECT_DIR {PROJECT_DIR}")

    rel = os.path.relpath(abs_path, PROJECT_DIR)
    if rel == ".":
        # Root folder request
        return "root"

    parts = rel.split(os.sep)
    parent = "root" # Start at root (MyDrive)

    # Cache cho folder id để đỡ query lại nhiều lần (nếu chạy loop)
    # Tuy nhiên function này stateless, nên ta chỉ retry trong từng step.

    for i, name in enumerate(parts):
        is_last = (i == len(parts) - 1)

        # Retry logic per level (để đợi Drive index folder/file mới tạo)
        found_id = None
        for attempt in range(3): # Try 3 times
            q = (
                f"name = '{_escape_q_val(name)}' and "
                f"'{parent}' in parents and trashed = false"
            )
            if not is_last:
                # Nếu không phải cấp cuối, chắc chắn phải là folder
                q += " and mimeType = 'application/vnd.google-apps.folder'"

            # Nếu là cấp cuối, nó có thể là file hoặc folder (zip)

            res = drive.files().list(
                q=q,
                fields="files(id,name,mimeType,parents,modifiedTime,createdTime)",
                pageSize=1,
                orderBy="modifiedTime desc",
                supportsAllDrives=True,
                includeItemsFromAllDrives=True
            ).execute().get("files", [])

            if res:
                found_id = res[0]["id"]
                break

            time.sleep(1) # Wait 1s before retry

        if not found_id:
            # Nếu không tìm thấy ở cấp nào đó -> fail toàn bộ
            return None

        parent = found_id

    return parent  # id phần tử cuối

def drive_public_link_for_local_path(abs_path: str, max_wait: int = 180, prefer_download: bool = False) -> str:
    """
    Trả về link công khai cho file tại abs_path.
    - Đợi Drive index file tối đa max_wait giây.
    - Tự tạo quyền 'anyone: reader' nếu chưa có.
    - prefer_download=True -> trả về link tải trực tiếp (webContentLink) nếu có.
    """
    if DRIVE is None:
        return ""

    t0 = time.time()
    file_id = None
    while time.time() - t0 < max_wait:
        file_id = drive_find_id_by_path(DRIVE, abs_path)
        if file_id:
            break
        time.sleep(2)

    if not file_id:
        print(f"⚠️ Không tìm thấy fileId trên Drive cho: {abs_path}")
        return ""

    # Chỉ tạo quyền nếu chưa có 'anyone'
    try:
        perms = DRIVE.permissions().list(
            fileId=file_id,
            fields="permissions(id,type,role)"
        ).execute().get("permissions", [])
        if not any(p.get("type") == "anyone" for p in perms):
            DRIVE.permissions().create(
                fileId=file_id,
                body={"type": "anyone", "role": "reader"},
            ).execute()
    except HttpError:
        pass

    meta = DRIVE.files().get(
        fileId=file_id,
        fields="id, webViewLink, webContentLink"
    ).execute()

    if prefer_download and meta.get("webContentLink"):
        return meta["webContentLink"]
    return meta.get("webViewLink", f"https://drive.google.com/file/d/{file_id}/view?usp=sharing")

def get_random_music_file(folder_config: str) -> str:
    """
    Tìm và tải ngẫu nhiên 1 file nhạc mp3 từ folder_config (ID hoặc tên).
    Trả về đường dẫn file local (cache).
    """
    if not folder_config: return None

    # 1. Thử coi nó là ID/URL không
    fid = extract_drive_id(folder_config)

    # 2. Nếu không phải ID, thử tìm theo tên trong PROJECT_DIR
    if not fid and DRIVE:
        fid = drive_find_id_by_path(DRIVE, os.path.join(PROJECT_DIR, folder_config))
        if not fid:
             # Thử tìm ở root nếu không thấy
             fid = drive_find_id_by_path(DRIVE, os.path.join(BASE_DRIVE, folder_config))

    # 3. Nếu vẫn không có FID nhưng folder tồn tại local (trường hợp chạy local không drive)
    if not fid:
        # Check local paths
        candidates = [
            os.path.join(PROJECT_DIR, folder_config),
            folder_config
        ]
        for p in candidates:
            if os.path.exists(p) and os.path.isdir(p):
                files = [os.path.join(p, f) for f in os.listdir(p) if f.lower().endswith(".mp3")]
                if files: return random.choice(files)
        return None

    # 4. Nếu có FID -> Dùng Drive API list và download
    if fid and DRIVE:
        try:
            q = f"'{fid}' in parents and (mimeType contains 'audio/' or name contains '.mp3') and trashed=false"
            res = DRIVE.files().list(q=q, fields="files(id, name)", pageSize=100).execute()
            files = res.get("files", [])

            if not files: return None

            chosen = random.choice(files)
            # Download to Cache
            safe_name = safe_slug(chosen['name'], 'bgm')
            # Fix extension
            if not safe_name.lower().endswith(".mp3"): safe_name += ".mp3"

            local_path = os.path.join(CACHE_DIR, "bg_music", f"{chosen['id']}_{safe_name}")

            if not os.path.exists(local_path):
                 if not os.path.exists(os.path.dirname(local_path)):
                     os.makedirs(os.path.dirname(local_path), exist_ok=True)

                 print(f"📥 Downloading Music: {chosen['name']}...")
                 from googleapiclient.http import MediaIoBaseDownload
                 request = DRIVE.files().get_media(fileId=chosen['id'])
                 fh = io.FileIO(local_path, 'wb')
                 downloader = MediaIoBaseDownload(fh, request)
                 done = False
                 while not done:
                     status, done = downloader.next_chunk()
                 fh.close()

            return local_path
        except Exception as e:
            print(f"⚠️ Error downloading music from Drive: {e}")
            return None

    return None

# ================== TIỆN ÍCH ==================
def extract_drive_id(url: str) -> str:
    if not url: return None
    match = re.search(r'[-\w]{25,}', url)
    return match.group(0) if match else None

def download_video_from_url(url: str, cache_name: str) -> str:
    if not url or not url.startswith("http"): return None
    path = os.path.join(CACHE_DIR, cache_name)
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return path
    safe_print(f"📥 Downloading asset: {url} -> {cache_name}")

    # Handle Drive
    if "drive.google.com" in url:
        file_id = extract_drive_id(url)
        if file_id and DRIVE:
            from googleapiclient.http import MediaIoBaseDownload
            request = DRIVE.files().get_media(fileId=file_id)
            fh = io.FileIO(path, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            fh.close()
            return path

    # Handle Direct
    resp = SESSION.get(url, stream=True, timeout=HTTP_TIMEOUT)
    resp.raise_for_status()
    with open(path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    return path


def looks_like_image_url(s: str) -> bool:
    return isinstance(s,str) and s.startswith("http") and re.search(r"\.(jpg|jpeg|png|webp)(\?|$)", s, re.I)

def sha1(s: str) -> str:
    import hashlib
    return hashlib.sha1(s.encode("utf-8")).hexdigest()

def safe_slug(v: str, fallback: str) -> str:
    s = slugify(v) if v else ""
    return s if s else fallback

def normalize_space(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())

def to_sheet_link(url: str) -> str:
    """Helper to format link for writing to Sheet (just return URL or formula)"""
    if not url: return ""
    if USE_HYPERLINK_FORMULA:
        return f'=HYPERLINK("{url}","{HYPERLINK_TEXT}")'
    return url

# ================== GOOGLE TTS (CÓ CACHE) — DROP-IN THAY VBEE ==================

def _guess_language_from_voice_name(voice_name: str, default_lang: str = "vi-VN") -> str:
    """Suy đoán language_code từ tên voice Google, ví dụ: 'vi-VN-Neural2-A' -> 'vi-VN'"""
    try:
        parts = voice_name.split("-")
        if len(parts) >= 2:
            return f"{parts[0]}-{parts[1]}"
    except:
        pass
    return default_lang

def vbee_tts_get_audio_path(input_text: str,
                            voice_code: str,
                            audio_type: str,
                            bitrate: int,
                            speed_rate: str) -> str:
    """
    DROP-IN: cùng tên và cùng tham số như Vbee, nhưng synth bằng Google Cloud TTS (REST + API key).
    - voice_code  : tên voice Google, ví dụ 'vi-VN-Neural2-A' (hoặc 'vi-VN-Wavenet-A')
    - audio_type  : 'mp3' hoặc 'wav' (wav = LINEAR16)
    - bitrate     : (ignored)
    - speed_rate  : chuỗi '1.0' -> speaking_rate
    Trả về: đường dẫn audio đã cache (CACHE_TTS_DIR).
    """
    if not GOOGLE_TTS_API_KEY:
        raise RuntimeError("Chưa có GOOGLE_TTS_API_KEY. Hãy đặt biến môi trường hoặc sửa GOOGLE_TTS_API_KEY ở phần CONFIG.")

    voice_name = str(voice_code or "vi-VN-Neural2-A").strip()
    language_code = _guess_language_from_voice_name(voice_name, "vi-VN")
    atype = str(audio_type or "mp3").lower()
    if atype not in ("mp3", "wav"):
        atype = "mp3"
    try:
        speaking_rate = float(speed_rate)
    except:
        speaking_rate = 1.0

    # Cache key (bỏ qua bitrate)
    key = f"REST|{voice_name}|{language_code}|{atype}|{speaking_rate}|{input_text}"
    h = sha1(key)
    ext = "mp3" if atype == "mp3" else "wav"
    cached_path = os.path.join(CACHE_TTS_DIR, f"{h}.{ext}")
    if os.path.exists(cached_path) and os.path.getsize(cached_path) > 0:
        return cached_path

    # --- CHULK LOGIC (FIX 400 Bad Request if text > 5000 bytes) ---
    MAX_BYTES = 4500 # Safety limit (API limit is 5000)
    
    # 1. Split into chunks
    chunks = []
    text_bytes_len = len(input_text.encode('utf-8'))
    
    if text_bytes_len < MAX_BYTES:
        chunks.append(input_text)
    else:
        # Split by sentences
        sentences = split_into_sentences(input_text)
        current_chunk = ""
        for s in sentences:
            # Estimate length if added
            next_chunk = (current_chunk + " " + s).strip()
            if len(next_chunk.encode('utf-8')) < MAX_BYTES:
                current_chunk = next_chunk
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = s
        if current_chunk:
            chunks.append(current_chunk)
            
    if not chunks:
        # Fallback if empty
        chunks = [" "]

    # 2. Call API for each chunk & Concatenate
    combined_audio = b""
    
    url = f"{GOOGLE_TTS_ENDPOINT}?key={GOOGLE_TTS_API_KEY}"
    audio_encoding = "MP3" if atype == "mp3" else "LINEAR16"

    for i, chunk_text in enumerate(chunks):
        if not chunk_text.strip(): continue
        
        body = {
            "input": {"text": chunk_text},
            "voice": {"languageCode": language_code, "name": voice_name},
            "audioConfig": {
                "audioEncoding": audio_encoding,
                "speakingRate": speaking_rate,
                "pitch": 0.0,
                "volumeGainDb": 0.0
            }
        }

        try:
            r = SESSION.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(body), timeout=HTTP_TIMEOUT)
            r.raise_for_status()
            data = r.json()
            audio_b64 = data.get("audioContent")
            if not audio_b64:
                print(f"⚠️ TTS chunk {i+1}/{len(chunks)} failed (no content)")
                continue
            
            combined_audio += base64.b64decode(audio_b64)
            # Add a small silence if needed? (optional, usually TTS has some padding)
            
        except requests.exceptions.HTTPError as e:
            # If 400 and Bad Request, maybe chunk still too big?
            print(f"❌ TTS Error chunk {i+1}: {e}")
            raise e

    # 3. Save Combined
    with open(cached_path, "wb") as f:
        f.write(combined_audio)

    return cached_path

# ================== ẢNH: CACHE + PREP ==================

def cache_image_path(url: str) -> str:
    h = sha1(url)
    return os.path.join(CACHE_IMG_DIR, f"{h}.jpg")

def cache_prepared_image_path_for_local(local_path: str) -> str:
    h = sha1("LOCAL|" + os.path.abspath(local_path))
    return os.path.join(CACHE_IMG_PREP_DIR, f"{h}.jpg")

def download_image_to_cache(url: str) -> str:
    path = cache_image_path(url)
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return path
    try:
        resp = SESSION.get(url, timeout=HTTP_TIMEOUT)
        resp.raise_for_status()
    except requests.HTTPError as e:
        # Fallback nhẹ cho Wikimedia
        if ("upload.wikimedia.org" in url) and (e.response is not None) and (e.response.status_code in (403, 429)):
            resp = requests.get(
                url,
                timeout=HTTP_TIMEOUT,
                headers={
                    "User-Agent": "GoogleTTSVideoBot/1.0 (Colab) +mailto:butlersamanthasya579@hotmail.com",
                    "Accept": "image/*",
                    "Referer": "https://commons.wikimedia.org/"
                }
            )
            resp.raise_for_status()
        else:
            raise
    try:
        img = Image.open(io.BytesIO(resp.content)).convert("RGB")
    except UnidentifiedImageError:
        raise ValueError("Ảnh không hợp lệ hoặc định dạng không hỗ trợ")
    img.save(path, format="JPEG", quality=92)
    return path

def fit_image_to_canvas(img: Image.Image, W=VIDEO_W, H=VIDEO_H) -> Image.Image:
    # Nền blur fill khung 9:16 + giữ tỉ lệ ảnh
    bg = img.copy().resize((W, H)).filter(ImageFilter.GaussianBlur(radius=20))
    iw, ih = img.size
    scale = min(W/iw, H/ih)
    new_w, new_h = int(iw*scale), int(ih*scale)
    img2 = img.resize((new_w, new_h), Image.LANCZOS)
    canvas = bg.copy()
    canvas.paste(img2, ((W-new_w)//2, (H-new_h)//2))
    return canvas

def prepare_image_from_local(raw_path: str) -> str:
    """Tạo phiên bản đã fit 1080x1920 từ file local -> trả về path ảnh đã chuẩn bị."""
    prep_path = cache_prepared_image_path_for_local(raw_path)
    if os.path.exists(prep_path) and os.path.getsize(prep_path) > 0:
        return prep_path
    with Image.open(raw_path).convert("RGB") as img:
        canvas = fit_image_to_canvas(img, VIDEO_W, VIDEO_H)
        canvas.save(prep_path, format="JPEG", quality=92)
    return prep_path

# ================== XỬ LÝ CÂU + KEN BURNS ==================
_SENT_SPLIT_RE = re.compile(r'(?<=[\.\!\?…])\s+|\n+')

def split_into_sentences(text: str) -> List[str]:
    text = normalize_space(text)
    if not text:
        return []
    parts = [p.strip() for p in _SENT_SPLIT_RE.split(text) if p and p.strip()]
    # gộp câu quá ngắn với câu trước cho đỡ vụn
    merged = []
    for p in parts:
        if merged and len(p) < 15:
            merged[-1] = merged[-1] + " " + p
        else:
            merged.append(p)
    return merged

def durations_from_sentences(sentences: List[str], total_dur: float, min_per_seg: float = 1.2) -> List[float]:
    if not sentences:
        return [total_dur]
    lens = [max(1, len(s)) for s in sentences]
    s = float(sum(lens))
    raw = [total_dur * (l / s) for l in lens]
    raw = [max(min_per_seg, d) for d in raw]
    scale = total_dur / sum(raw)
    return [d * scale for d in raw]


def make_ken_burns_clip_from_path(img_path: str, duration: float, seed: int = 0):
    """
    Ken Burns mượt bằng CompositeVideoClip: zoom 3%~8%, pan 4 hướng.
    Hoạt động chính xác trên khung dọc 1080x1920.
    """
    random.seed(seed + RANDOM_SEED_BASE)
    W, H = VIDEO_W, VIDEO_H
    zoom_in = (seed % 2 == 0)
    z_start = random.uniform(KB_MIN_ZOOM, KB_MAX_ZOOM)
    z_end   = 1.0 if zoom_in else random.uniform(KB_MIN_ZOOM, KB_MAX_ZOOM)
    if zoom_in:
        z0, z1 = 1.0, z_start
    else:
        z0, z1 = z_start, 1.0

    direction = seed % 4  # 0 L->R, 1 R->L, 2 T->B, 3 B->T

    def scale_fn(t):
        prog = t / max(1e-4, duration)
        return z0 + (z1 - z0) * prog

    def pos_fn(t):
        prog = t / max(1e-4, duration)
        s = scale_fn(t)
        sw, sh = W * s, H * s
        if direction in (0, 1):  # ngang
            y = (H - sh) / 2.0
            x = (W - sw) * (prog if direction == 0 else (1 - prog))
        else:  # dọc
            x = (W - sw) / 2.0
            y = (H - sh) * (prog if direction == 2 else (1 - prog))
        return (x, y)

    img_clip = ImageClip(img_path).set_duration(duration)
    kb_moving = img_clip.resize(lambda t: scale_fn(t)).set_position(lambda t: pos_fn(t))
    comp = CompositeVideoClip([kb_moving], size=(W, H)).fadein(FADE_IN).fadeout(FADE_OUT)
    return comp
# ================== BUILD VIDEO CHO 1 DÒNG (KHÔNG SUB) ==================

def output_name_for_row(row: dict, idx: int) -> str:
    title = str(row.get(COL_TITLE, f"video_{idx}")).strip()
    return f"{safe_slug(title, f'video_{idx+1}')}.mp4"

def build_video_for_row(row: dict, idx: int) -> Tuple[str, Dict[str, str]]:
    """
    Trả về (out_path, wiki_drive_links)
    - out_path: đường dẫn video mp4 xuất ra
    - wiki_drive_links: map {col_name: drive_link} cho các ảnh Wikimedia đã mirror (phục vụ write-back)
    """
    title = normalize_space(str(row.get(COL_TITLE, f"video_{idx}")))
    desc  = normalize_space(str(row.get(COL_DESC, "") or title))

    # Overrides theo dòng (nếu sheet có cột)
    row_voice = (str(row.get("voice_code", "")).strip() or VBEE_VOICE)
    row_speed = (str(row.get("speed_rate", "")).strip() or VBEE_SPEED)
    row_atype = (str(row.get("audio_type", "")).strip() or VBEE_AUDIO_TYPE)
    row_br    = row.get("bitrate", "") or VBEE_BITRATE
    try: row_br = int(row_br)
    except: row_br = VBEE_BITRATE

    # Thu thập URL ảnh đầu vào
    input_urls = [str(row.get(c,"")).strip() for c in IMAGE_COLS if str(row.get(c,"")).strip()]
    if not any(looks_like_image_url(u) for u in input_urls):
        raise ValueError(f"Dòng {idx+1} không có ảnh hợp lệ.")

    # Chuẩn bị ảnh (tải trực tiếp từ các URL trong sheet)
    prepared_img_paths: List[str] = []
    wiki_drive_links: Dict[str, str] = {}

    for c in IMAGE_COLS:
        val = str(row.get(c, "")).strip()
        if not val:
            continue
        try:
            if looks_like_image_url(val):
                raw_path = download_image_to_cache(val)
                prepared_img_paths.append(prepare_image_from_local(raw_path))
        except Exception as e:
            print(f"⚠️ Lỗi ảnh {c} ({val}): {e}")

    if not prepared_img_paths:
        raise ValueError("Không tạo được ảnh đã chuẩn bị nào.")

    # TTS (có cache) — dùng Google REST qua vbee_tts_get_audio_path
    audio_cached_path = vbee_tts_get_audio_path(desc, row_voice, row_atype, row_br, row_speed)
    audio_ext = audio_cached_path.split(".")[-1]
    audio_path = os.path.join(OUTPUT_DIR, f"{safe_slug(title, f'video_{idx+1}')}_voice.{audio_ext}")
    if not os.path.exists(audio_path):
        shutil.copy2(audio_cached_path, audio_path)

    # Durations
    audio_clip = None
    total_dur = DEFAULT_PER_IMAGE * len(prepared_img_paths)
    try:
        audio_clip = AudioFileClip(audio_path)
        total_dur = float(audio_clip.duration)
    except Exception:
        pass

    # Chia nhỏ theo câu
    sentences = split_into_sentences(desc)
    per_seg_durs = durations_from_sentences(sentences if sentences else [desc], total_dur, min_per_seg=1.2)

    # Tạo các clip Ken Burns theo từng đoạn/câu
    clips = []
    video = None
    try:
        for si, dur in enumerate(per_seg_durs):
            img_path = prepared_img_paths[si % len(prepared_img_paths)]
            kb_clip = make_ken_burns_clip_from_path(img_path, dur, seed=si)
            clips.append(kb_clip)

        video = concatenate_videoclips(clips, method="compose").set_fps(FPS)

        # Gắn audio + cân thời lượng cho khít
        if audio_clip:
            diff = audio_clip.duration - video.duration
            if abs(diff) > 0.05:
                if diff > 0 and len(clips) > 0:
                    last = clips[-1].set_duration(clips[-1].duration + diff)
                    video = concatenate_videoclips(clips[:-1] + [last], method="compose").set_fps(FPS)
                elif diff < 0:
                    video = video.subclip(0, max(0.05, audio_clip.duration)).set_fps(FPS)
            video = video.set_audio(audio_clip)

        # Xuất file (chưa merge voice) -> để merge music
        # Tuy nhiên ở trên ta đã set_audio(voice) rồi.
        # Giờ ta sẽ mix thêm nhạc nền.

        # --- BACKGROUND MUSIC LOGIC ---
        music_file = get_random_music_file(MUSIC_DRIVE_FOLDER)
        if music_file and audio_clip:
            try:
                # Load music
                # Cần copy về local để moviepy load nhanh
                music_local_path = os.path.join(CACHE_DIR, "bg_music", os.path.basename(music_file))
                if not os.path.exists(music_local_path):
                    if not os.path.exists(os.path.dirname(music_local_path)):
                         os.makedirs(os.path.dirname(music_local_path), exist_ok=True)
                    # Copy from Drive
                    shutil.copy2(music_file, music_local_path)

                music_clip = AudioFileClip(music_local_path)

                # Loop music to match video duration
                # Nếu music ngắn hơn video -> loop
                # Nếu dài hơn -> cắt
                if music_clip.duration < video.duration:
                    # Loop
                    n_loops = int(video.duration / music_clip.duration) + 1
                    music_clip = concatenate_videoclips([music_clip] * n_loops).audio
                    music_clip = music_clip.set_duration(video.duration)
                else:
                    music_clip = music_clip.subclip(0, video.duration)

                # Set Volume (0.1 ~ 0.2)
                music_clip = music_clip.volumex(MUSIC_VOLUME)

                # Mix Voice + Music
                # voice_audio (từ video.audio hoặc audio_clip gốc)
                final_audio = CompositeAudioClip([audio_clip, music_clip])
                video = video.set_audio(final_audio)

                print(f"🎵 Added background music: {os.path.basename(music_file)}")
            except Exception as e:
                print(f"⚠️ Failed to add music: {e}")

        # Xuất file
        out_path = os.path.join(OUTPUT_DIR, f"{output_name_for_row(row, idx)}")
        video.write_videofile(
            out_path,
            codec="libx264",
            audio_codec="aac",
            fps=FPS,
            bitrate="6000k",
            threads=4,
            ffmpeg_params=["-movflags", "+faststart", "-preset", "fast"],
            verbose=False,
            logger=None
        )
        return out_path, wiki_drive_links
    finally:
        try:
            if audio_clip: audio_clip.close()
        except: pass
        for c in clips:
            try: c.close()
            except: pass
        try:
            if video: video.close()
        except: pass
        gc.collect()

# ================== SHEET BATCH UPDATE ==================

def batch_update_cells(ws, updates, chunk_size=200, value_input_option="RAW"):
    """updates: list of {'range': 'A1', 'values': [[...]]}"""
    if not ws or not updates:
        return
    for i in range(0, len(updates), chunk_size):
        part = updates[i:i+chunk_size]
        ws.batch_update(part, value_input_option=value_input_option)

# ================== CHẠY TOÀN BỘ — BỎ QUA DÒNG ĐÃ DONE ==================
# ================== WHISPER SUBTITLES & PARALLEL PROCESSING ==================
import whisper
from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"}) # Default Colab ImageMagick

# Hàm lấy timestamp từ file audio bằng Whisper
def get_transcription(audio_path, model_name="small"):
    # Load model (có thể cache model bên ngoài nếu muốn)
    # Tuy nhiên trong ThreadPool, load model nhiều lần sẽ tốn VRAM.
    # Tốt nhất là load model 1 lần global nếu chạy tuần tự,
    # nhưng vì chạy song song, ta cần cẩn thận VRAM.
    # Giải pháp: Dùng model nhỏ hoặc load global + lock (nhưng Whisper không thread-safe lắm).
    # -> Load global model, chạy transcribe tuần tự (lock), hoặc mỗi thread tự load (tốn RAM).
    # -> Tối ưu nhất cho Colab: 1 Global Model, dùng Lock khi transcribe.
    pass

# Global Lock cho Whisper và Print để tránh loạn output
import threading
from concurrent.futures import ThreadPoolExecutor

PRINT_LOCK = threading.Lock()
WHISPER_LOCK = threading.Lock()
SHEET_LOCK = threading.Lock()

# Load model 1 lần (nếu có GPU thì load cuda, không thì cpu)
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"🚀 Loading Whisper model ({device})...")
model = whisper.load_model("small", device=device)

def safe_print(*args, **kwargs):
    with PRINT_LOCK:
        print(*args, **kwargs)

def generate_subtitles_clips(audio_path, video_w, video_h):
    """
    Dùng Whisper lấy word-level timestamps -> Tạo TextClip
    Trả về list các TextClips (MoviePy)
    """
    with WHISPER_LOCK:
        result = model.transcribe(audio_path, word_timestamps=True)

    segments = result.get('segments', [])
    subtitle_clips = []

    # Font style - NỔI BẬT HƠN
    font_size = 70               # Tăng kích thước (cũ 50)
    stroke_width = 4             # Viền dày hơn (cũ 2)
    stroke_color = '#FF0000'     # Viền ĐỎ (Red)
    color = '#FFFFFF'            # Màu TRẮNG (White)

    # --- FIX FONT TIẾNG VIỆT ---
    # Tải font Google (Roboto Bold) về để chắc chắn hỗ trợ tiếng Việt
    font_path = os.path.join(CACHE_DIR, "Roboto-Bold.ttf")
    if not os.path.exists(font_path):
        try:
            # Link tải font Roboto-Bold
            url_font = "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf"
            r = requests.get(url_font, allow_redirects=True)
            with open(font_path, 'wb') as f:
                f.write(r.content)
            print(f"✅ Đã tải font: {font_path}")
        except Exception as e:
            print(f"⚠️ Không tải được font, dùng mặc định: {e}")
            font_path = 'Arial-Bold' # Fallback

    # Sử dụng font_path nếu có, ngược lại dùng string hệ thống
    if os.path.exists(font_path):
        font_arg = font_path
    else:
        font_arg = 'Arial-Bold' # Hy vọng hệ thống có

    for seg in segments:
        for word in seg.get('words', []):
            start = word['start']
            end = word['end']
            text = word['word'].strip()

            # Tạo TextClip (cần ImageMagick)
            # stroke_width giúp nổi bật trên nền động
            txt_clip = (TextClip(text, fontsize=font_size, color=color,
                                 stroke_color=stroke_color, stroke_width=stroke_width, font=font_arg,
                                 method='caption', size=(video_w*0.9, None)) # Caption method để wrap text nếu dài
                        .set_position(('center', 0.8*video_h)) # Vị trí dưới cùng
                        .set_start(start)
                        .set_end(end))
            subtitle_clips.append(txt_clip)

    return subtitle_clips

# ================== DRIVE UPLOAD HELPER ==================
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

def upload_file_to_drive(local_path, parent_id, drive_service):
    """Uploads a file to a specific Drive folder and returns webViewLink."""
    if not os.path.exists(local_path): return None

    file_metadata = {
        'name': os.path.basename(local_path),
        'parents': [parent_id]
    }
    media = MediaFileUpload(local_path, resumable=True)

    try:
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink, webContentLink',
            supportsAllDrives=True
        ).execute()

        # Set public permission
        try:
            drive_service.permissions().create(
                fileId=file.get('id'),
                body={'type': 'anyone', 'role': 'reader'},
            ).execute()
        except: pass

        return file.get('webViewLink')
    except Exception as e:
        print(f"❌ Upload failed for {local_path}: {e}")
        return None


# ================== YOUTUBE UPLOAD HELPER ==================
def upload_video_to_youtube(file_path, title, description, category_id, privacy_status, youtube_service):
    """
    Uploads a video to YouTube using resumable upload.
    Returns: video_id (str) or None if failed.
    """
    if not os.path.exists(file_path):
        print(f"❌ YouTube Upload: File not found {file_path}")
        return None

    body = {
        'snippet': {
            'title': title, # YouTube max 100 chars
            'description': description, # YouTube max 5000 chars
            'tags': ['audiobook', 'sachnoi', 'vbee'],
            'categoryId': category_id
        },
        'status': {
            'privacyStatus': privacy_status,
            'selfDeclaredMadeForKids': False,
        }
    }

    # Resumable upload
    media = MediaFileUpload(file_path, chunksize=1024*1024, resumable=True)

    try:
        request = youtube_service.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"   ⬆️ YouTube Uploading: {int(status.progress() * 100)}%")

        vid_id = response.get('id')
        print(f"✅ YouTube Upload Complete! Video ID: {vid_id}")
        return vid_id

    except Exception as e:
        print(f"❌ YouTube Upload Error: {e}")
        return None

# ================== PROCESS SINGLE ROW (WORKER) ==================
def process_row(index, row):
    try:
        sheet_row_number = index + 2

        # Check SKIP
        status_val = str(row.get(STATUS_COL, "")).strip().upper()

        # In upload mode, we check logic differently or just always process if not DONE
        # Output name is still relevant
        out_name = output_name_for_row(row, index)
        out_full_path = os.path.join(OUTPUT_DIR, out_name)

        # If DONE, skip
        if status_val == "DONE":
             safe_print(f"⏩ Skip row {sheet_row_number}: DONE.")
             return

        # If not DONE but file exists locally?
        if os.path.exists(out_full_path):
             # If local existing, maybe we just need to upload?
             pass

        safe_print(f"▶️ Processing row {sheet_row_number} - {out_name}...")

        # 1. Build Base Video (Images + Audio + Ken Burns)
        out_path, wiki_links = build_video_for_row(row, index)

        # 2. Add Subtitles (Whisper) logic (omitted for brevity, assume `out_path` is final)
        # Using the same logic as before for consistency...
        title_slug = safe_slug(normalize_space(str(row.get(COL_TITLE, f"video_{index}"))), f'video_{index+1}')
        # Try finding the audio file (mp3 or wav)
        audio_candidate_mp3 = os.path.join(OUTPUT_DIR, f"{title_slug}_voice.mp3")
        audio_candidate_wav = os.path.join(OUTPUT_DIR, f"{title_slug}_voice.wav")
        audio_path_final = None

        if os.path.exists(audio_candidate_mp3):
            audio_path_final = audio_candidate_mp3
        elif os.path.exists(audio_candidate_wav):
            audio_path_final = audio_candidate_wav

        final_out_path = out_path

        if audio_path_final and os.path.exists(audio_path_final):
            try:
                safe_print(f"   Creating subtitles for {out_name}...")
                sub_clips = generate_subtitles_clips(audio_path_final, VIDEO_W, VIDEO_H)
                if sub_clips:
                    # Load video
                    video_clip = VideoFileClip(out_path)
                    # Overlay subtitles
                    video_with_subs = CompositeVideoClip([video_clip] + sub_clips)

                    # Write to a temp file then rename or overwrite
                    # Rename original to _nosub
                    no_sub_path = out_path.replace(".mp4", "_nosub.mp4")
                    os.rename(out_path, no_sub_path)

                    video_with_subs.write_videofile(
                        out_path, # Overwrite main target
                        codec="libx264",
                        audio_codec="aac",
                        fps=FPS,
                        bitrate="6000k",
                        threads=2, # Reduce threads per worker
                        ffmpeg_params=["-preset", "fast"],
                        verbose=False,
                        logger=None
                    )

                    # Cleanup
                    video_clip.close()
                    video_with_subs.close()
                    # Optional: delete nosub file to save space
                    if os.path.exists(no_sub_path):
                        os.remove(no_sub_path)

                    final_out_path = out_path
            except Exception as e:
                safe_print(f"⚠️ Failed to add subtitles for {out_name}: {e}")
                # Fallback to original video (which is now at no_sub_path if rename succeeded)
                if os.path.exists(out_path.replace(".mp4", "_nosub.mp4")):
                     if os.path.exists(out_path):
                         os.remove(out_path) # Failed write?
                     os.rename(out_path.replace(".mp4", "_nosub.mp4"), out_path)

                final_out_path = out_path

        # 2.5 Add Intro / Outro (Concatenate)
        if ENABLE_INTRO_OUTRO:
            try:
                # Tìm/Tải file Intro/Outro
                intro_p = download_video_from_url(INTRO_URL, "intro_asset.mp4")
                outro_p = download_video_from_url(OUTRO_URL, "outro_asset.mp4")

                # Nút fallback nếu link trống nhưng vẫn muốn tìm local (như cũ)
                if not intro_p:
                     for p in [os.path.join(PROJECT_DIR, "intro.mp4"), "intro.mp4"]:
                         if os.path.exists(p): intro_p = p; break
                if not outro_p:
                     for p in [os.path.join(PROJECT_DIR, "outro.mp4"), "outro.mp4"]:
                         if os.path.exists(p): outro_p = p; break


                if intro_p or outro_p:
                    safe_print(f"   🎬 Adding Intro/Outro ({'Intro' if intro_p else ''} {'Outro' if outro_p else ''})...")

                    clips_to_concat = []

                    # Helper resize
                    def prepare_clip(path):
                        c = VideoFileClip(path)
                        # Resize/Crop to 1080x1920
                        # Nếu tỷ lệ khác -> Crop center
                        c_ratio = c.w / c.h
                        target_ratio = VIDEO_W / VIDEO_H

                        if c.w != VIDEO_W or c.h != VIDEO_H:
                             if c_ratio > target_ratio:
                                 # Ảnh rộng hơn -> resize theo cao, crop ngang
                                 c = c.resize(height=VIDEO_H)
                                 c = c.crop(x1=(c.w - VIDEO_W)/2, width=VIDEO_W)
                             else:
                                 # Ảnh cao hơn -> resize theo rộng, crop dọc
                                 c = c.resize(width=VIDEO_W)
                                 c = c.crop(y1=(c.h - VIDEO_H)/2, height=VIDEO_H)
                        return c

                    # Intro
                    if intro_p:
                        clips_to_concat.append(prepare_clip(intro_p))

                    # Body (Final Output from previous step)
                    current_body = VideoFileClip(final_out_path)
                    clips_to_concat.append(current_body)

                    # Outro
                    if outro_p:
                        clips_to_concat.append(prepare_clip(outro_p))

                    # Concatenate with Fade (Crossfadein ko chạy tốt với audio đôi khi, dùng simple compose)
                    # Hoặc method="compose"
                    final_seq = concatenate_videoclips(clips_to_concat, method="compose")

                    # Write to new file
                    concat_path = final_out_path.replace(".mp4", "_full.mp4")
                    final_seq.write_videofile(
                        concat_path,
                        codec="libx264", audio_codec="aac", fps=FPS,
                        threads=2, preset="fast", verbose=False, logger=None
                    )

                    # Replace final Output
                    # Clean up body clip usage
                    current_body.close()
                    for c in clips_to_concat:
                         # Don't close Body again if it's there? No, VideoFileClip instances are distinct
                         try: c.close()
                         except: pass

                    # Swap
                    if os.path.exists(concat_path):
                        if os.path.exists(final_out_path): os.remove(final_out_path)
                        os.rename(concat_path, final_out_path)

            except Exception as e:
                safe_print(f"⚠️ Intro/Outro Error: {e}")

        # 3. Upload & Sync Sheet
        safe_print(f"   Finishing {out_name}...")

        public_link = ""
        yt_link = ""

        # --- DRIVE UPLOAD ---
        if UPLOAD_MODE and TARGET_FOLDER_ID:
            safe_print(f"   ⬆️ Uploading to Drive Folder {TARGET_FOLDER_ID}...")
            # Upload to Drive API
            uplink = upload_file_to_drive(final_out_path, TARGET_FOLDER_ID, DRIVE)
            if uplink:
                public_link = uplink
                # Optional: Delete local temp file to save space in Colab
                # os.remove(final_out_path)
            else:
                safe_print(f"⚠️ Drive Upload failed, keeping local file.")
                public_link = drive_public_link_for_local_path(final_out_path, max_wait=60, prefer_download=PUBLIC_LINK_DIRECT_DOWNLOAD)

        else:
            # Mount Mode
            public_link = drive_public_link_for_local_path(final_out_path, max_wait=60, prefer_download=PUBLIC_LINK_DIRECT_DOWNLOAD) or os.path.basename(final_out_path)

        # --- YOUTUBE UPLOAD (NEW) ---
        if UPLOAD_TO_YOUTUBE and YOUTUBE:
            safe_print(f"   ⬆️ Uploading to YouTube...")
            vid_title = normalize_space(str(row.get(COL_TITLE, f"video_{index}")))[:100]
            vid_desc  = normalize_space(str(row.get(COL_DESC, "") or vid_title))[:5000]

            # Nếu có Drive Link, append vào description
            if public_link:
                vid_desc += f"\n\nDownload: {public_link}"

            vid_id = upload_video_to_youtube(final_out_path, vid_title, vid_desc, YOUTUBE_CATEGORY_ID, YOUTUBE_PRIVACY, YOUTUBE)
            if vid_id:
                yt_link = f"https://youtu.be/{vid_id}"
                safe_print(f"   ✅ YouTube Link: {yt_link}")
            else:
                safe_print(f"   ⚠️ YouTube Upload Failed.")

        # Update Sheet (Thread-safe)
        if ws is not None:
            with SHEET_LOCK:
                # Re-verify row data to ensure we are writing to the correct place if insertion happened (rare in this usecase)
                # But strict index-based update update_cell(date_row, ...) is safe if no rows deleted.
                ws.update_cell(sheet_row_number, col_idx[STATUS_COL], "DONE")
                if DRIVE_COL in col_idx:
                    ws.update_cell(sheet_row_number, col_idx[DRIVE_COL], to_sheet_link(public_link))

                if OUTPUT_COL in col_idx and yt_link:
                    ws.update_cell(sheet_row_number, col_idx[OUTPUT_COL], to_sheet_link(yt_link))
                elif OUTPUT_COL in col_idx and not yt_link:
                    # Nếu không có link YouTube, vẫn ghi link Drive vào Output nếu cột Drive ko tồn tại?
                    # Để an toàn, nếu ko có YouTube thì Output giữ Drive link làm fallback nếu user muốn.
                    if DRIVE_COL not in col_idx:
                        ws.update_cell(sheet_row_number, col_idx[OUTPUT_COL], to_sheet_link(public_link))

                if MIRROR_WRITE_BACK_TO_SHEET and wiki_links:
                    for c, dlink in wiki_links.items():
                         if c in col_idx and dlink:
                            ws.update_cell(sheet_row_number, col_idx[c], to_sheet_link(dlink))

        safe_print(f"✅ Finished row {sheet_row_number}: Drive={public_link} YouTube={yt_link}")
        return final_out_path

    except Exception as e:
        safe_print(f"❌ Error row {index+2}: {e}")
        return None

# ================== RUN PARALLEL ==================
# Số luồng (Colab 2 vCPU -> 2-3 threads là đẹp, nhiều quá tốn RAM load ảnh)
# Update: Giảm xuống 2 để tránh crash RAM khi chạy cùng Whisper
# ================== RUN CAMPAIGN (CONTINUOUS LOGIC) ==================

def run_campaign():
    global ws, df, DRIVE, YOUTUBE

    print("\n🔄 [Campaign] Reloading Sheet Data...")
    try:
        # Reload Sheet to get new rows
        ws, df, DRIVE, YOUTUBE = get_services(SHEET_ID, SHEET_NAME)
    except Exception as e:
        print(f"⚠️ Error reloading sheet: {e}")
        return

    if df.empty:
        print("⚠️ Sheet empty.")
        return

    # Filter rows that need processing
    pending_rows = []
    for i, row in df.iterrows():
        status = str(row.get(STATUS_COL, "")).strip().upper()
        # [MỚI] Kiểm tra xem đã có link chưa để bỏ qua
        drive_link = str(row.get(DRIVE_COL, "")).strip()
        pub_link = str(row.get(OUTPUT_COL, "")).strip()

        # Chỉ xử lý dòng chưa DONE và chưa có link video nào
        if status != "DONE" and not drive_link and not pub_link:
            pending_rows.append((i, row))
            if len(pending_rows) >= CAMPAIGN_MAX_ROWS_PER_LOOP:
                break

    if not pending_rows:
        print("✅ No pending rows found (Status != DONE).")
    else:
        print(f"🚀 Found {len(pending_rows)} pending rows. Starting processing...")

        # Số luồng (Colab 2 vCPU -> 2 threads là an toàn nhất với Whisper)
        MAX_WORKERS = 1

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [executor.submit(process_row, i, row) for i, row in pending_rows]
            for future in futures:
                future.result()

        print("🏁 Batch processing finished.")

    # ================== ZIP OUTPUT (OPTIONAL) ==================
    # Only zip if NOT in Upload Mode (Mount Mode)
    # Because in Upload Mode we upload individual files directly.
    if not UPLOAD_MODE and pending_rows:
        import zipfile

        def list_artifacts(dir_path: str):
            vids = []
            for n in sorted(os.listdir(dir_path)):
                p = os.path.join(dir_path, n)
                if os.path.isfile(p) and (n.lower().endswith(".mp4") or n.lower().endswith(".mp3")):
                    vids.append(p)
            return vids

        def free_space_bytes(path="/"):
            total, used, free = shutil.disk_usage(path)
            return free

        def make_zip_safely(files, out_zip_path, max_zip_bytes=None):
            if not files: return []
            created = []
            part = 1
            cur_batch = []
            cur_est = 0
            limit = max_zip_bytes or 0

            def _write_zip(batch_files, zip_path):
                if os.path.exists(zip_path): os.remove(zip_path)
                with zipfile.ZipFile(zip_path, mode="w", compression=zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
                    for fp in batch_files:
                        zf.write(fp, arcname=os.path.basename(fp))
                return zip_path

            for fp in files:
                sz = os.path.getsize(fp)
                if limit and cur_batch and (cur_est + sz > limit):
                    zip_path = out_zip_path if part == 1 else out_zip_path.replace(".zip", f"_part{part}.zip")
                    if free_space_bytes("/") < cur_est + 65536: raise OSError("No space left")
                    created.append(_write_zip(cur_batch, zip_path))
                    part += 1
                    cur_batch, cur_est = [], 0
                cur_batch.append(fp)
                cur_est += sz

            if cur_batch:
                zip_path = out_zip_path if part == 1 else out_zip_path.replace(".zip", f"_part{part}.zip")
                if free_space_bytes("/") < cur_est + 65536: raise OSError("No space left")
                created.append(_write_zip(cur_batch, zip_path))
            return created

        artifacts = list_artifacts(OUTPUT_DIR)
        if artifacts:
            zip_base = os.path.join(OUTPUT_DIR, "videos_google_tts_output")
            zip_path = f"{zip_base}.zip"
            try:
                zips = make_zip_safely(artifacts, zip_path, max_zip_bytes=1_800_000_000)
                for zp in zips:
                    link = drive_public_link_for_local_path(zp, max_wait=180, prefer_download=PUBLIC_LINK_DIRECT_DOWNLOAD)
                    print(f"📦 ZIP Created: {zp} -> {link}")
            except OSError as e:
                print(f"⚠️ Zip failed (disk space): {e}")

# ================== MAIN EXECUTION LOOP ==================

if __name__ == "__main__":
    print(f"🎬 VIDEO GENERATOR STARTED")
    print(f"ℹ️  Continuous Mode: {CONTINUOUS_MODE}")
    print(f"ℹ️  Check Interval: {CHECK_INTERVAL}s")

    while True:
        run_campaign()

        if not CONTINUOUS_MODE:
            print("⏹️ Continuous Mode OFF. Stopping.")
            break

        print(f"\n⏳ Sleeping {CHECK_INTERVAL} seconds (15 mins)...")
        print("👉 Please KEEP THIS TAB OPEN.")
        try:
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            print("🛑 Stopped by user.")
            break
