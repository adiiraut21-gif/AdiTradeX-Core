from flask import Blueprint, jsonify, render_template, request
from technical_pro.service import (
    get_multi_timeframe_data,
    get_timeframe_snapshot,
    get_trend_intelligence,
    get_momentum_intelligence,
    get_vwap_intelligence,
    get_structure_intelligence,
    get_technical_intelligence_snapshot
)

technical_pro_bp = Blueprint("technical_pro", __name__)

@technical_pro_bp.route("/")
def technical_pro_dashboard():
    underlying = request.args.get("underlying", "nifty")
    try:
        snapshot = get_technical_intelligence_snapshot(underlying)
        trend = get_trend_intelligence(underlying)
        momentum = get_momentum_intelligence(underlying)
        vwap = get_vwap_intelligence(underlying)
        structure = get_structure_intelligence(underlying)
        return render_template("technical_pro_dashboard.html", snapshot=snapshot, trend=trend, momentum=momentum, vwap=vwap, structure=structure, error=None)
    except Exception as e:
        return render_template("technical_pro_dashboard.html", snapshot=None, trend=None, momentum=None, vwap=None, structure=None, error=str(e))

@technical_pro_bp.route("/trend/<underlying>")
def trend_json(underlying):
    try:
        return jsonify(get_trend_intelligence(underlying))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@technical_pro_bp.route("/momentum/<underlying>")
def momentum_json(underlying):
    try:
        return jsonify(get_momentum_intelligence(underlying))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@technical_pro_bp.route("/vwap/<underlying>")
def vwap_json(underlying):
    try:
        return jsonify(get_vwap_intelligence(underlying))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@technical_pro_bp.route("/structure/<underlying>")
def structure_json(underlying):
    try:
        return jsonify(get_structure_intelligence(underlying))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@technical_pro_bp.route("/snapshot/<underlying>")
def snapshot_json(underlying):
    try:
        return jsonify(get_technical_intelligence_snapshot(underlying))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

@technical_pro_bp.route("/candles/<underlying>/<timeframe>")
def technical_pro_candles(underlying, timeframe):
    try:
        return jsonify(get_timeframe_snapshot(underlying, timeframe))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
