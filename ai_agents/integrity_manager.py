import os
import subprocess
import socket
import requests
import shutil # Moved from check_disk_space
import logging
from datetime import datetime
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_now_hanoi

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logging.warning("psutil not found. System stats will be unavailable.")

class IntegrityManagerAgent:
    def __init__(self):
        self.logger = logging.getLogger("integrity_manager")
        self.reports_dir = "/app/reports" if os.path.exists("/app") else "reports"
        os.makedirs(self.reports_dir, exist_ok=True)
        # Email Notifier
        try:
            from utils.email_notifier import EmailNotifier
            self.notifier = EmailNotifier()
        except ImportError:
            self.notifier = None
            print("⚠️ Could not import EmailNotifier")

    def check_health_endpoint(self, url="http://localhost:5001/health"):
        """Checks if the internal server is responding."""
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200 and resp.json().get("status") == "healthy":
                return True, "Server is healthy."
            return False, f"Server returned status {resp.status_code}: {resp.text}"
        except Exception as e:
            return False, f"Could not reach health endpoint: {e}"

    def check_disk_space(self, path="/", threshold_percent=90):
        """Checks if disk space is running low."""
        import shutil
        total, used, free = shutil.disk_usage(path)
        percent = (used / total) * 100
        if percent > threshold_percent:
            return False, f"Disk space critical: {percent:.1f}% used."
        return True, f"Disk space OK: {percent:.1f}% used."

    def check_memory_usage(self, threshold_percent=90):
        """Checks if memory usage is too high, with fallbacks."""
        try:
            import psutil
            mem = psutil.virtual_memory()
            if mem.percent > threshold_percent:
                return False, f"Memory usage critical: {mem.percent}% used."
            return True, f"Memory usage OK: {mem.percent}% used."
        except Exception as e:
            # Fallback for when psutil fails (e.g. restricted env)
            return True, f"Memory check skipped (psutil error: {str(e)})"

    def run_diagnostics(self):
        """Runs all diagnostic checks and returns results."""
        results = []
        
        # 1. Check Server Health
        h_ok, h_msg = self.check_health_endpoint()
        results.append({"check": "Server Health", "status": "PASS" if h_ok else "FAIL", "message": h_msg})
        
        # 2. Check Disk
        d_ok, d_msg = self.check_disk_space()
        results.append({"check": "Disk Space", "status": "PASS" if d_ok else "FAIL", "message": d_msg})
        
        # 3. Check Memory
        m_ok, m_msg = self.check_memory_usage()
        results.append({"check": "Memory Usage", "status": "PASS" if m_ok else "FAIL", "message": m_msg})
        
        return results

    def perform_healing(self, diagnostic_results):
        """Attempts to fix identified issues."""
        actions_taken = []
        
        for res in diagnostic_results:
            if res["status"] == "FAIL":
                if "Disk space critical" in res["message"]:
                    # Try to prune docker if in docker environment or just log
                    actions_taken.append("Clean-up suggestion: Run 'docker system prune -f' on host.")
                
                if "Could not reach health endpoint" in res["message"]:
                    # In a real environment with Docker socket, we could restart.
                    # Here we log it as a critical failure requiring orchestrator attention.
                    actions_taken.append("Critical: AI Backend unresponsive. Recommending orchestrator restart.")

        return actions_taken

    def generate_report(self, results, actions):
        """Generates a markdown report of the integrity check."""
        timestamp = get_now_hanoi().strftime("%Y-%m-%d %H:%M:%S")
        report = f"# 🛡️ Báo cáo Bảo trì Hệ thống (Integrity Report)\n\n"
        report += f"**Thời gian kiểm tra**: `{timestamp}`\n\n"
        
        report += "## 🔍 Kết quả Chẩn đoán\n"
        report += "| Kiểm tra | Trạng thái | Chi tiết |\n"
        report += "| :--- | :--- | :--- |\n"
        for r in results:
            icon = "✅" if r["status"] == "PASS" else "❌"
            report += f"| {r['check']} | {icon} {r['status']} | {r['message']} |\n"
        
        report += "\n## 🛠️ Hành động Khắc phục\n"
        if not actions:
            report += "Hệ thống hoạt động hoàn hảo. Không cần can thiệp.\n"
        else:
            for a in actions:
                report += f"- {a}\n"
        
        report += "\n---\n*Được tạo tự động bởi Integrity Manager Agent.*"
        
        filename = os.path.join(self.reports_dir, f"integrity_report_latest.md")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)
        
        return filename

    def run(self):
        """Main entry point for the agent."""
        print("🛡️ [Integrity Agent] Bắt đầu kiểm tra hệ thống...")
        results = self.run_diagnostics()
        actions = self.perform_healing(results)
        report_path = self.generate_report(results, actions)
        print(f"✅ [Integrity Agent] Đã hoàn thành. Báo cáo lưu tại: {report_path}")
        
        # Send Email
        if self.notifier:
            with open(report_path, "r", encoding="utf-8") as f:
                content = f.read()
            # Simple conversion for email
            html_content = f"<html><body><pre>{content}</pre></body></html>"
            self.notifier.send_report("🛡️ [Integrity] Báo cáo Hệ thống", html_content)
            
        return report_path

if __name__ == "__main__":
    agent = IntegrityManagerAgent()
    agent.run()
