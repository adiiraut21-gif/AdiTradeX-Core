from flask import Blueprint, jsonify, render_template
from market.service import get_index_quotes, fetch_quotes, normalize_quote, save_market_snapshot, latest_snapshots, resolve_symbol, safe_index_quotes

market_bp = Blueprint("market", __name__)

@market_bp.route("/indices")
def indices():
    try:
        return jsonify(get_index_quotes())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@market_bp.route("/indices/save")
def indices_save():
    try:
        quotes = get_index_quotes()
        save_market_snapshot(quotes)
        return jsonify({"status": "saved", "count": len(quotes), "data": quotes})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@market_bp.route("/quote/<path:symbol>")
def quote(symbol):
    try:
        resolved = resolve_symbol(symbol)
        raw = fetch_quotes([resolved])
        return jsonify({s: normalize_quote(s, q) for s, q in raw.items()})
    except Exception as e:
        return jsonify({"error": str(e), "symbol": symbol}), 500

@market_bp.route("/snapshots")
def snapshots():
    return jsonify(latest_snapshots())

@market_bp.route("/dashboard")
def market_dashboard():
    quotes, error = safe_index_quotes()
    return render_template("market_dashboard.html", quotes=quotes, error=error)
