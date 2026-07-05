from flask import Blueprint, jsonify, render_template, request
from technical_pro.service import get_multi_timeframe_data, get_timeframe_snapshot, get_trend_intelligence

technical_pro_bp = Blueprint("technical_pro", __name__)

@technical_pro_bp.route("/")
def technical_pro_dashboard():
    underlying = request.args.get("underlying", "nifty")
    try:
        data = get_trend_intelligence(underlying)
        return render_template("technical_pro_dashboard.html", data=data, error=None)
    except Exception as e:
        return render_template("technical_pro_dashboard.html", data=None, error=str(e))

@technical_pro_bp.route("/data/<underlying>")
def technical_pro_data_page(underlying):
    try:
        data = get_multi_timeframe_data(underlying, include_candles=False)
        return render_template("technical_pro_data_dashboard.html", data=data, error=None)
    except Exception as e:
        return render_template("technical_pro_data_dashboard.html", data=None, error=str(e))

@technical_pro_bp.route("/json/<underlying>")
def technical_pro_json(underlying):
    include = request.args.get("include_candles", "false").lower() == "true"
    try:
        return jsonify(get_multi_timeframe_data(underlying, include_candles=include))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@technical_pro_bp.route("/trend/<underlying>")
def trend_json(underlying):
    try:
        return jsonify(get_trend_intelligence(underlying))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@technical_pro_bp.route("/candles/<underlying>/<timeframe>")
def technical_pro_candles(underlying, timeframe):
    try:
        return jsonify(get_timeframe_snapshot(underlying, timeframe))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
