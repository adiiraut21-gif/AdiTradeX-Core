from position.position_sync import fetch_open_positions
from position.position_technical import technical_confirmation
from position.position_option_chain import option_chain_confirmation
from position.position_risk import build_risk_plan
from position.position_decision import make_position_decision

def analyze_position(position):
    technical = technical_confirmation(position)
    option_chain = option_chain_confirmation(position)
    risk = build_risk_plan(position, technical, option_chain)
    decision = make_position_decision(position, technical, option_chain, risk)

    return {
        "position": position,
        "technical": technical,
        "option_chain": option_chain,
        "risk": risk,
        "decision": decision
    }

def get_position_intelligence():
    sync = fetch_open_positions()
    results = [analyze_position(p) for p in sync.get("positions", [])]

    return {
        "status": "ok",
        "count": len(results),
        "positions": results
    }
