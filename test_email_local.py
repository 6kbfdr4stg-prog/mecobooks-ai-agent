import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.email_notifier import EmailNotifier

# Manually set credentials for this test session (from user input)
os.environ["EMAIL_SENDER"] = "chuthihong6272@gmail.com"
os.environ["EMAIL_PASSWORD"] = "tsmn izhi uasa vdjq"

def test_email():
    print("📧 Đang thử gửi email test...")
    notifier = EmailNotifier()
    
    subject = "🧪 Kiem tra he thong Email - Mecobooks AI Agent"
    body = """
    <html>
        <body>
            <h2 style="color: #2F80ED;">Test thành công! 🚀</h2>
            <p>Xin chào,</p>
            <p>Đây là email kiểm tra từ hệ thống <b>Mecobooks AI Agent</b>.</p>
            <p>Nếu bạn nhận được email này, nghĩa là tính năng báo cáo tự động đã hoạt động hoàn hảo.</p>
            <hr>
            <p><i>Integrity Manager Agent</i></p>
        </body>
    </html>
    """
    
    notifier.send_report(subject, body)

if __name__ == "__main__":
    test_email()
