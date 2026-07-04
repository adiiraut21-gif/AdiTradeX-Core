import sqlite3
from config.settings import Settings

def get_connection():
    return sqlite3.connect(Settings.DATABASE_PATH)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        user_name TEXT,
        access_token TEXT,
        login_time TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS event_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type TEXT,
        message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()

def log_event(event_type, message):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO event_logs (event_type, message) VALUES (?, ?)", (event_type, message))
    conn.commit()
    conn.close()
