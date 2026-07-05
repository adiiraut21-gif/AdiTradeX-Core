from flask import Blueprint, jsonify, render_template, request
from strategy.service import build_strategy_decision

strategy_bp = Blueprint("strategy", __name__)

@strategy_bp.route("/")
def strategy_dashboard():
    underlying = request.args.get("underlying", "nifty")
    interval = request.args.get("interval", "15m")
    try:
        data = build_strategy_decision(underlying, interval)
        return render_template("strategy_dashboard.html", data=data, error=None)
    except Exception as e:
        return render_template("strategy_dashboard.html", data=None, error=str(e))

@strategy_bp.route("/json/<underlying>")
def strategy_json(underlying):
    interval = request.args.get("interval", "15m")
    try:
        return jsonify(build_strategy_decision(underlying, interval))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
