"""
Master Overseer Agent - Phase 12
Giám sát toàn bộ 9 Agent trong hệ thống, ghi log thời gian chạy,
phát hiện Agent chết (Heartbeat) và tổng hợp báo cáo Daily Digest.
"""
import os
import sys
import time
import logging
import datetime
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from ai_agents.telegram_client import send_telegram_message

LOG_DB_URL = os.path.join(BASE_DIR, "agent_logs.db")

def get_log_db_connection():
    conn = sqlite3.connect(LOG_DB_URL, timeout=10)
    conn.execute('PRAGMA journal_mode=WAL;')
    conn.row_factory = sqlite3.Row
    return conn

def init_log_db():
    conn = get_log_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS agent_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_name TEXT,
            status TEXT,
            message TEXT,
            duration_seconds REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize right away
init_log_db()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("overseer")

# Define expected agents and their expected frequency in hours (for Heartbeat test)
# If an agent hasn't logged a success in this timeframe, it triggers an alert.
EXPECTED_AGENTS = {
    "content_creator": 14,      # runs 2x a day
    "market_research": 74,      # runs every 3 days
    "inventory_analyst": 170,   # runs weekly
    "pricing_strategy": 26,     # runs daily
    "bi_analyst": 26,           # runs daily
    "strategic_analyst": 170,   # runs weekly
    "integrity_manager": 2,     # runs hourly
    "auto_debug": 26,           # runs daily
    "bundle_sync": 1,           # runs every 15 min
}

class OverseerAgent:
    def __init__(self):
        self.conn = get_log_db_connection()

    def _get_agent_status(self, limit: int = 50):
        """Fetch the latest execution logs for all agents."""
        c = self.conn.cursor()
        c.execute('''
            SELECT agent_name, status, message, duration_seconds, timestamp
            FROM agent_logs
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        return [dict(row) for row in c.fetchall()]

    def check_heartbeats(self):
        """
        Check if any scheduled agents have missed their expected run window.
        Sends a Telegram alert if an agent is dead.
        """
        logger.info("💓 Overseer is checking agent heartbeats...")
        c = self.conn.cursor()
        
        dead_agents = []
        for agent_name, max_hours in EXPECTED_AGENTS.items():
            # Get the last successful run for this agent
            c.execute('''
                SELECT timestamp FROM agent_logs 
                WHERE agent_name = ? AND status = 'SUCCESS' 
                ORDER BY timestamp DESC LIMIT 1
            ''', (agent_name,))
            row = c.fetchone()
            
            if row:
                last_run_str = row['timestamp']
                # SQLite timestamp is UTC
                try:
                    last_run = datetime.datetime.strptime(last_run_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    # try with microseconds if present
                    try:
                        last_run_str = last_run_str.split('.')[0]
                        last_run = datetime.datetime.strptime(last_run_str, "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        continue
                
                hours_since = (datetime.datetime.utcnow() - last_run).total_seconds() / 3600
                if hours_since > max_hours:
                    dead_agents.append(f"• **{agent_name}**: quá hạn tĩnh lạng {hours_since:.1f}h (Ngưỡng: {max_hours}h)")
            else:
                 # Never run yet
                 dead_agents.append(f"• **{agent_name}**: Chưa ghi nhận log nào trong DB!")

        if dead_agents:
            msg = "🚨 **OVERSEER ALERT: PHÁT HIỆN AGENT CHẾT LÂM SÀNG!** 🚨\n\nCác hệ thống sau đã quá hạn lịch trình chuẩn xác mà không có phản hồi:\n"
            msg += "\n".join(dead_agents)
            msg += "\n\nVui lòng kiểm tra server logs."
            logger.warning("Dead agents detected! Sending Telegram alert.")
            send_telegram_message(msg)
        else:
            logger.info("✅ All agents are beating perfectly.")

    def generate_daily_digest(self):
        """
        Generate a master summary at 21:00 compiling everything the agents did today.
        """
        logger.info("📋 Overseer is generating the Master Daily Digest...")
        today_start = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        c = self.conn.cursor()
        
        c.execute('''
            SELECT agent_name, status, message
            FROM agent_logs
            WHERE timestamp >= ?
            ORDER BY timestamp ASC
        ''', (today_start.strftime("%Y-%m-%d %H:%M:%S"),))
        
        logs = c.fetchall()
        
        if not logs:
            send_telegram_message("👁️ **Overseer Daily Digest**\n\nHôm nay hệ thống AI không có hoạt động nào được ghi nhận.")
            return

        total_runs = len(logs)
        successes = len([row for row in logs if row['status'] == 'SUCCESS'])
        errors = total_runs - successes
        
        msg = f"👁️ **OVERSEER MASTER DAILY DIGEST** 👁️\n\n"
        msg += f"📊 **Tổng quan Năng suất AI Hôm Nay:**\n"
        msg += f"• Tổng lượt kích hoạt: {total_runs}\n"
        msg += f"• Thành công: {successes} ✅\n"
        msg += f"• Lỗi/Thất bại: {errors} ❌\n\n"
        
        msg += f"📝 **Tóm tắt Hoạt Động:**\n"
        
        # Group by agent
        agent_actions = {}
        for row in logs:
            name = row['agent_name']
            if name not in agent_actions:
                agent_actions[name] = {'success': 0, 'error': 0}
            
            if row['status'] == 'SUCCESS':
                agent_actions[name]['success'] += 1
            else:
                agent_actions[name]['error'] += 1

        for name, stats in agent_actions.items():
            icon = "✅" if stats['error'] == 0 else "⚠️"
            msg += f"• **{name}**: {stats['success']} lượt chạy {icon}\n"
            if stats['error'] > 0:
                msg += f"  └ Kèm {stats['error']} lượt báo lỗi.\n"
        
        send_telegram_message(msg)
        logger.info("✅ Daily Digest sent.")

# ─── LOGGING DECORATOR FOR SCHEDULER ──────────────────────────────────────────
def log_agent_execution(agent_name: str):
    """
    Decorator to wrap scheduler jobs. It measures execution time,
    catches unhandled exceptions, and writes the log to the SQLite database.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            status = 'SUCCESS'
            message = "Completed successfully."
            
            try:
                # Run the actual agent job
                result = func(*args, **kwargs)
                if result:
                    message = str(result)[:500] # truncate long messages
            except Exception as e:
                status = 'ERROR'
                message = f"Failed with exception: {traceback.format_exc()}"[:500]
                logger.error(f"Agent {agent_name} failed: {e}")
            finally:
                duration = time.time() - start_time
                try:
                    # Write to database
                    conn = get_log_db_connection()
                    conn.execute('''
                        INSERT INTO agent_logs (agent_name, status, message, duration_seconds)
                        VALUES (?, ?, ?, ?)
                    ''', (agent_name, status, message, duration))
                    conn.commit()
                    conn.close()
                except Exception as log_err:
                    logger.error(f"Overseer failed to write log for {agent_name}: {log_err}")
                
            return result
        return wrapper
    return decorator


if __name__ == '__main__':
    overseer = OverseerAgent()
    print("Testing Heartbeat...")
    overseer.check_heartbeats()
    print("Testing Daily Digest...")
    overseer.generate_daily_digest()
