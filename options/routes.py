from flask import Blueprint, jsonify, render_template, request
from options.service import build_option_chain, get_nfo_instruments

options_bp = Blueprint("options", __name__)

@options_bp.route("/")
def options_home():
    underlying = request.args.get("underlying", "nifty")
    try:
        data = build_option_chain(underlying)
        return render_template("option_chain.html", data=data, error=None)
    except Exception as e:
        return render_template("option_chain.html", data=None, error=str(e))

@options_bp.route("/chain/<underlying>")
def option_chain_json(underlying):
    try:
        return jsonify(build_option_chain(underlying))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@options_bp.route("/reload-instruments")
def reload_instruments():
    try:
        instruments = get_nfo_instruments(force_refresh=True)
        return jsonify({"status": "reloaded", "count": len(instruments)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
