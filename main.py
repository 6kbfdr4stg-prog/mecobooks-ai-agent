import subprocess
import time
import sys
import os

def start_system():
    print("🌟 [MASTER] Kích hoạt Hệ thống AI Agent - Tiệm Sách Anh Tuấn")
    print("---------------------------------------------------------")

    # 1. Start Server (Chatbot 24/7)
    print("🚀 Khởi động Sales Support Server (Cổng 5001)...")
    env = os.environ.copy()
    env["PORT"] = "5001"
    server_process = subprocess.Popen([sys.executable, "server.py"], env=env)

    # 2. Wait for server to stabilize
    time.sleep(3)

    # 3. Start Scheduler (Background Agents: Content, Inventory, Strategy)
    print("⏰ Khởi động Background Agent Scheduler...")
    scheduler_process = subprocess.Popen([sys.executable, "scheduler.py"])

    print("\n✅ Hệ thống đã sẵn sàng!")
    print("- Chatbot: Hoạt động (Web/FB)")
    print("- Scheduler: Đang chạy (Content/Inventory/Strategy)")
    print("---------------------------------------------------------")

    try:
        while True:
            # Monitor processes
            if server_process.poll() is not None:
                print("⚠️ Server stopped! Restarting...")
                server_process = subprocess.Popen([sys.executable, "server.py"])
            
            if scheduler_process.poll() is not None:
                print("⚠️ Scheduler stopped! Restarting...")
                scheduler_process = subprocess.Popen([sys.executable, "scheduler.py"])
                
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n🛑 Đang dừng hệ thống...")
        server_process.terminate()
        scheduler_process.terminate()
        print("Done.")

if __name__ == "__main__":
    start_system()
