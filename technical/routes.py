from flask import Blueprint, jsonify, render_template, request
from technical.service import analyze_technical

technical_bp = Blueprint("technical", __name__)

@technical_bp.route("/")
def technical_dashboard():
    underlying = request.args.get("underlying", "nifty")
    interval = request.args.get("interval", "15m")
    try:
        data = analyze_technical(underlying, interval)
        return render_template("technical_dashboard.html", data=data, error=None)
    except Exception as e:
        return render_template("technical_dashboard.html", data=None, error=str(e))

@technical_bp.route("/json/<underlying>")
def technical_json(underlying):
    interval = request.args.get("interval", "15m")
    try:
        return jsonify(analyze_technical(underlying, interval))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
