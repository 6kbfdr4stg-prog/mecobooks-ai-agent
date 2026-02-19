import sqlite3
from datetime import datetime
from ai_agents.telegram_client import send_telegram_message

def simulate_agent_run():
    agent_name = "content_creator"
    timestamp = datetime.now().strftime('%Y%m%d%H%M')
    filename = f"{agent_name}_{timestamp}.md"
    
    # 1. Hợp nội dung mẫu (Markdown)
    md_content = f"""# ✍️ Marketing Content: Đắc Nhân Tâm (How to Win Friends and Influence People)

**Sản phẩm:** Đắc Nhân Tâm - Dale Carnegie
**Giá:** 89,000 VNĐ

### 📱 Facebook/Instagram Caption

🌟 "Nghệ thuật cao nhất là làm cho người khác yêu mến mình."

Bạn đã bao giờ tự hỏi tại sao có những người luôn tỏa ra một sức hút kỳ lạ, khiến ai gặp cũng thấy mến, ai nói chuyện cũng thấy tin? Bí mật không nằm ở tài năng bẩm sinh, mà nằm ở sự thấu hiểu lòng người.

Cuốn sách **"Đắc Nhân Tâm"** không chỉ là một tựa sách bán chạy nhất mọi thời đại, mà còn là một "kim chỉ nam" cho bất kỳ ai muốn xây dựng những mối quan hệ chân thành và bền vững. Với lối kể chuyện giản dị nhưng sâu sắc, Dale Carnegie sẽ đưa bạn đi từ những nguyên tắc giao tiếp nhỏ nhất đến những thay đổi lớn lao trong tư duy.

✨ Hãy cùng dừng lại một chút, lật mở những trang sách và tìm thấy phiên bản tốt đẹp hơn của chính mình nhé.

----
📍 Link mình để dưới comment để cả nhà dễ tìm nhé!
#MecoBooks #DacNhanTam #SachHay #GiaoTiep #Storytelling

### 🎬 Video Script (Shorts/Reels)

**(00:00 - 00:05)** Bạn cảm thấy lạc lõng trong các buổi trò chuyện? Hay muốn được đồng nghiệp nể trọng hơn?
**(00:05 - 00:15)** Đắc Nhân Tâm không chỉ dạy bạn cách "lấy lòng", mà dạy bạn cách "thấu hiểu". 
**(00:15 - 00:25)** Chỉ với 3 nguyên tắc vàng đầu tiên, bạn sẽ thấy thế giới xung quanh thay đổi kỳ diệu.
**(00:25 - 00:35)** Cuốn sách gối đầu giường của hàng triệu người thành công. Đừng chỉ đọc, hãy cảm nhận và thực hành ngay hôm nay!
**(00:35 - 00:40)** Bấm vào link bên dưới để sở hữu ngay nhé!

---
*Nội dung được tạo tự động bởi Mecobooks AI Agent.*
"""

    # 2. Lưu vào Database
    try:
        conn = sqlite3.connect('app.db')
        c = conn.cursor()
        c.execute("INSERT INTO reports (agent_name, report_type, content, created_at) VALUES (?, ?, ?, ?)",
                  (filename, "markdown", md_content, datetime.utcnow()))
        conn.commit()
        conn.close()
        print(f"✅ Đã lưu báo cáo mô phỏng vào Database: {filename}")
    except Exception as e:
        print(f"❌ Lỗi lưu Database: {e}")

    # 3. Gửi Telegram
    try:
        import html
        clean_snippet = html.escape(md_content[:400]) + "..."
        message = f"🚀 <b>[DEMO] Report Generated: {agent_name}</b>\n\n{clean_snippet}\n\n<a href='https://mecobooks-ai-agent.onrender.com/verify'>Xem trên Dashboard</a>"
        send_telegram_message(message)
        print("✅ Đã gửi thông báo Telegram.")
    except Exception as e:
        print(f"❌ Lỗi gửi Telegram: {e}")

if __name__ == "__main__":
    simulate_agent_run()
