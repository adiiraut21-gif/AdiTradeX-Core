from flask import Blueprint, jsonify, render_template, request
from analytics.service import analyze_underlying

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/")
def analytics_home():
    underlying = request.args.get("underlying", "nifty")
    try:
        data = analyze_underlying(underlying)
        return render_template("analytics_dashboard.html", data=data, error=None)
    except Exception as e:
        return render_template("analytics_dashboard.html", data=None, error=str(e))

@analytics_bp.route("/json/<underlying>")
def analytics_json(underlying):
    try:
        return jsonify(analyze_underlying(underlying))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route("/summary/<underlying>")
def analytics_summary(underlying):
    try:
        data = analyze_underlying(underlying)
        return jsonify({
            "underlying": data["underlying"],
            "summary": data["summary"],
            "bias": data["institutional_bias"],
            "confidence": data["confidence"],
            "trade_quality": data["trade_quality"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
