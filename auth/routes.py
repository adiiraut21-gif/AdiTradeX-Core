from flask import Blueprint, request, jsonify, render_template_string, redirect, url_for
from config.settings import Settings
from config.logger import setup_logger
from database.db import log_event
from auth.kite_client import get_kite_client
from auth.session_store import save_session, get_latest_session, clear_session

auth_bp = Blueprint("auth", __name__)
logger = setup_logger()

@auth_bp.route("/")
def home():
    kite = get_kite_client()
    login_url = kite.login_url()
    session = get_latest_session()
    status = "CONNECTED" if session else "NOT CONNECTED"

    return render_template_string("""
    <html><head><title>AdiTradeX Core</title>
    <style>
    body { font-family: Arial; background:#f7f7f7; margin:40px; }
    .card { background:white; padding:24px; border-radius:12px; max-width:760px; box-shadow:0 2px 10px rgba(0,0,0,.08); }
    .btn { display:inline-block; padding:12px 18px; background:#1f7a3a; color:white; text-decoration:none; border-radius:8px; font-weight:bold; }
    .status { padding:8px 12px; border-radius:6px; background:#eee; display:inline-block; }
    code { background:#eee; padding:3px 6px; border-radius:4px; }
    </style></head><body><div class="card">
    <h1>AdiTradeX Core v1.5</h1>
    <p><b>Status:</b> <span class="status">{{ status }}</span></p>
    <p>Core architecture upgrade: database session storage, logging, modular folders, and cleaner config.</p>
    <p><a class="btn" href="{{ login_url }}">Login with Zerodha</a></p>
    <hr>
    <p><code>/health</code> <code>/status</code> <code>/profile</code> <code>/dashboard</code></p>
    <p><b>Mode:</b> Read-only foundation. No order placement.</p>
    </div></body></html>
    """, status=status, login_url=login_url)

@auth_bp.route("/zerodha/callback")
def zerodha_callback():
    if not Settings.KITE_API_SECRET:
        return jsonify({"error": "KITE_API_SECRET missing in environment variables"}), 500

    status = request.args.get("status")
    request_token = request.args.get("request_token")

    if status != "success" or not request_token:
        return jsonify({
            "error": "Login failed or request_token missing.",
            "status": status,
            "action": request.args.get("action")
        }), 400

    try:
        kite = get_kite_client()
        data = kite.generate_session(request_token=request_token, api_secret=Settings.KITE_API_SECRET)

        access_token = data["access_token"]
        user_id = data.get("user_id")
        user_name = data.get("user_name")

        save_session(user_id, user_name, access_token)
        logger.info("Zerodha login successful for user_id=%s", user_id)

        return render_template_string("""
        <html><head><title>AdiTradeX Login Successful</title>
        <style>
        body { font-family: Arial; background:#f7f7f7; margin:40px; }
        .card { background:white; padding:24px; border-radius:12px; max-width:760px; box-shadow:0 2px 10px rgba(0,0,0,.08); }
        .ok { color:green; font-weight:bold; }
        code { background:#eee; padding:3px 6px; border-radius:4px; }
        </style></head><body><div class="card">
        <h1 class="ok">Login Successful</h1>
        <p>AdiTradeX Core is connected to Zerodha for today's session.</p>
        <p><b>User:</b> {{ user_name }}</p>
        <p><b>User ID:</b> {{ user_id }}</p>
        <hr>
        <p>Now test: <code>/status</code>, <code>/profile</code>, and <code>/dashboard</code></p>
        <p><a href="/">Back to Home</a></p>
        </div></body></html>
        """, user_name=user_name, user_id=user_id)

    except Exception as e:
        logger.exception("Access token generation failed")
        log_event("ERROR", f"Access token generation failed: {str(e)}")
        return jsonify({"error": "Could not generate access token.", "details": str(e)}), 500

@auth_bp.route("/status")
def status():
    session = get_latest_session()
    return jsonify({
        "connected": bool(session),
        "session": {
            "user_id": session["user_id"],
            "user_name": session["user_name"],
            "login_time": session["login_time"],
        } if session else None,
        "api_key_loaded": bool(Settings.KITE_API_KEY),
        "api_secret_loaded": bool(Settings.KITE_API_SECRET),
        "version": Settings.VERSION
    })

@auth_bp.route("/profile")
def profile():
    session = get_latest_session()
    if not session:
        return jsonify({"error": "Not logged in. Open / and login first."}), 401

    try:
        kite = get_kite_client(session["access_token"])
        return jsonify(kite.profile())
    except Exception as e:
        logger.exception("Profile fetch failed")
        return jsonify({"error": "Could not fetch Kite profile", "details": str(e)}), 500

@auth_bp.route("/logout")
def logout():
    clear_session()
    return redirect(url_for("auth.home"))
