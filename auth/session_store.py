from datetime import datetime
from database.db import get_connection, log_event

def save_session(user_id, user_name, access_token):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM sessions")
    cur.execute(
        "INSERT INTO sessions (user_id, user_name, access_token, login_time) VALUES (?, ?, ?, ?)",
        (user_id, user_name, access_token, datetime.now().isoformat(timespec="seconds"))
    )
    conn.commit()
    conn.close()
    log_event("AUTH", f"Zerodha session connected for {user_id}")

def get_latest_session():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id, user_name, access_token, login_time FROM sessions ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "user_id": row[0],
        "user_name": row[1],
        "access_token": row[2],
        "login_time": row[3],
    }

def clear_session():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM sessions")
    conn.commit()
    conn.close()
    log_event("AUTH", "Zerodha session cleared")
