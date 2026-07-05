def strategy_readiness(institutional_score, ev_score, risk_level):
    if risk_level == "Low" and institutional_score >= 85 and ev_score >= 75:
        return {
            "strategy_ready": "YES",
            "message": "Setup is ready for Strategy Decision Engine"
        }

    if risk_level == "Medium" and institutional_score >= 75:
        return {
            "strategy_ready": "CAUTION",
            "message": "Use only defined-risk spread after confirmation"
        }

    if risk_level == "High":
        return {
            "strategy_ready": "WATCHLIST",
            "message": "Wait for stronger confirmation"
        }

    return {
        "strategy_ready": "NO",
        "message": "Capital preservation preferred"
    }
