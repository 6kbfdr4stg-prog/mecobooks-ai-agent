from ai_agents.telegram_client import send_telegram_message

if __name__ == "__main__":
    test_message = "🚀 **Mecobooks AI Agent**\n\nKết nối thành công! Bạn sẽ nhận được báo cáo từ hệ thống tại đây."
    print("Sending test message...")
    send_telegram_message(test_message)
    print("Done.")
