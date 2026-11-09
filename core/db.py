import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "./data/leads.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                domain TEXT PRIMARY KEY,
                vulnerabilities TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

def is_lead_processed(domain: str) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT 1 FROM leads WHERE domain = ?", (domain,))
        return cursor.fetchone() is not None

def log_lead(domain: str, scraped_data: dict):
    vulns = str(scraped_data.get("vulnerabilities", []))
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO leads (domain, vulnerabilities) VALUES (?, ?)",
            (domain, vulns)
        )

