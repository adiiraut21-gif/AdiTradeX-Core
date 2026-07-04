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

    cur.execute('''
    CREATE TABLE IF NOT EXISTS market_snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT,
        last_price REAL,
        open_price REAL,
        high_price REAL,
        low_price REAL,
        close_price REAL,
        net_change REAL,
        volume INTEGER,
        oi INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()

def log_event(event_type, message):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO event_logs (event_type, message) VALUES (?, ?)",
        (event_type, message)
    )
    conn.commit()
    conn.close()

def latest_events(limit=20):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT event_type, message, created_at FROM event_logs ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cur.fetchall()
    conn.close()
    return [
        {"event_type": r[0], "message": r[1], "created_at": r[2]}
        for r in rows
    ]
