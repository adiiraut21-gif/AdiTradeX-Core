from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from config.settings import Settings
from config.logger import setup_logger
from database.db import log_event
from auth.kite_client import get_kite_client
from auth.session_store import save_session, get_latest_session, clear_session

auth_bp = Blueprint("auth", __name__)
logger = setup_logger()

@auth_bp.route("/")
def home():
    session = get_latest_session()
    kite = get_kite_client()
    return render_template(
        "login.html",
        session=session,
        login_url=kite.login_url(),
        version=Settings.VERSION
    )

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
        data = kite.generate_session(
            request_token=request_token,
            api_secret=Settings.KITE_API_SECRET
        )

        save_session(data.get("user_id"), data.get("user_name"), data["access_token"])
        logger.info("Zerodha login successful for user_id=%s", data.get("user_id"))

        return render_template(
            "login_success.html",
            user_name=data.get("user_name"),
            user_id=data.get("user_id")
        )
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
        return jsonify({"error": "Not logged in"}), 401

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
