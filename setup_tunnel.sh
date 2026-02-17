#!/bin/bash
# 1. Đi đến thư mục dự án
cd /Users/tuankth/.gemini/antigravity/scratch/video_project

# 2. Xóa file cũ nếu bị lỗi
rm -f cloudflared cloudflared-darwin-arm64.tgz

# 3. Tải bộ cài nén (.tgz) - Cách này ổn định nhất cho Mac
echo "Đang tải bộ cài Cloudflare (30MB)... Vui lòng đợi trong giây lát..."
curl -L -o cloudflared-darwin-arm64.tgz https://github.com/cloudflare/cloudflared/releases/download/2026.2.0/cloudflared-darwin-arm64.tgz

# 4. Giải nén
echo "Đang giải nén..."
tar -xzf cloudflared-darwin-arm64.tgz

# 5. Cấp quyền
chmod +x cloudflared

# 6. Bật đường ống
echo "---"
echo "BẮT ĐẦU MỞ ĐƯỜNG ỐNG..."
echo "Hãy copy link có đuôi '.trycloudflare.com' bên dưới!"
echo "---"
./cloudflared tunnel --url http://localhost:5001
