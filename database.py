import sqlite3
import os
from datetime import datetime

DATABASE_URL = "app.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_name TEXT,
            report_type TEXT,
            content TEXT,
            created_at TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

class Report:
    def __init__(self, id, agent_name, report_type, content, created_at):
        self.id = id
        self.agent_name = agent_name
        self.report_type = report_type
        self.content = content
        self.created_at = created_at

