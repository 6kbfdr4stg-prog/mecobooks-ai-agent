#!/bin/bash
echo "🚀 Đang bắt đầu quá trình chuyển đổi sang Docker..."
cd /Users/tuankth/.gemini/antigravity/scratch/video_project

# 1. Kiểm tra Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Lỗi: Máy bạn chưa cài đặt Docker hoặc Docker Desktop chưa được mở."
    exit 1
fi

# 2. Tắt các tiến trình cũ đang chiếm cổng 5001
echo "⚙️  Đang dọn dẹp các tiến trình cũ..."
lsof -ti:5001 | xargs kill -9 2>/dev/null || echo "Cổng 5001 đã sạch."

# 3. Build và Chạy Docker
echo "📦 Đang đóng gói và khởi chạy Docker (Quá trình này có thể mất 1-2 phút)..."
# Thêm lệnh dọn dẹp nếu build lỗi (Input/Output error thường do đầy bộ nhớ Docker)
if ! (docker compose up -d --build 2>/dev/null || docker-compose up -d --build); then
    echo "⚠️  Phát hiện lỗi Build. Đang thử dọn dẹp bộ nhớ Docker và thử lại..."
    docker system prune -f
    if docker compose version &> /dev/null; then
        docker compose up -d --build
    else
        docker-compose up -d --build
    fi
fi

# 4. Kiểm tra kết quả
echo "---"
if [ $? -eq 0 ]; then
    echo "✅ CHÚC MỪNG! AI Backend đã chạy trong Docker thành công."
    echo "Bạn có thể kiểm tra tại: http://localhost:5001/health"
    docker ps | grep ai_flywheel_backend
else
    echo "❌ Có lỗi xảy ra trong quá trình khởi chạy Docker."
fi
echo "---"
