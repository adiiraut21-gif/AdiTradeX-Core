from flask import Blueprint, render_template_string
from auth.session_store import get_latest_session

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
def dashboard():
    session = get_latest_session()
    connected = bool(session)

    return render_template_string("""
    <html><head><title>AdiTradeX Dashboard</title>
    <style>
    body { font-family: Arial; background:#0f172a; color:#e5e7eb; margin:40px; }
    .card { background:#111827; padding:24px; border-radius:14px; max-width:900px; box-shadow:0 2px 12px rgba(0,0,0,.35); }
    .ok { color:#22c55e; }
    .bad { color:#ef4444; }
    code { background:#1f2937; padding:4px 8px; border-radius:5px; }
    </style></head><body><div class="card">
    <h1>AdiTradeX Dashboard</h1>
    <h2 class="{{ 'ok' if connected else 'bad' }}">{{ "Connected to Zerodha" if connected else "Not Connected" }}</h2>
    {% if session %}
    <p><b>User:</b> {{ session.user_name }}</p>
    <p><b>User ID:</b> {{ session.user_id }}</p>
    <p><b>Login Time:</b> {{ session.login_time }}</p>
    {% endif %}
    <hr>
    <h3>Milestone 1.5 Status</h3>
    <p>✅ Modular architecture</p>
    <p>✅ SQLite session storage</p>
    <p>✅ Structured logging</p>
    <p>✅ Config layer</p>
    <p>✅ Read-only Zerodha auth</p>
    <hr>
    <p>Next module: <code>Milestone 2 - Live Market Data Engine</code></p>
    </div></body></html>
    """, connected=connected, session=session)
