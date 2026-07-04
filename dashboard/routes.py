from flask import Blueprint, render_template
from auth.session_store import get_latest_session
from database.db import latest_events
from market.service import safe_index_quotes

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
def dashboard():
    session = get_latest_session()
    quotes, market_error = safe_index_quotes() if session else ([], None)
    events = latest_events(12)

    return render_template(
        "dashboard.html",
        session=session,
        quotes=quotes,
        market_error=market_error,
        events=events
    )
