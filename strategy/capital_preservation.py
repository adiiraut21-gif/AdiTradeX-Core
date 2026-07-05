def capital_preservation_filter(institutional_score, engine_confidence, ev_score, risk_level=None):
    if institutional_score >= 85 and engine_confidence >= 70 and ev_score >= 75:
        return {
            "action": "PROCEED",
            "message": "Institutional-grade setup. Eligible for Strategy Decision Engine."
        }

    if institutional_score >= 75 and ev_score >= 65:
        return {
            "action": "PROCEED WITH CAUTION",
            "message": "Good setup, but use only defined-risk strategy after confirmation."
        }

    if institutional_score >= 65:
        return {
            "action": "WAIT",
            "message": "Watchlist only. Wait for stronger confirmation."
        }

    return {
        "action": "NO TRADE",
        "message": "Capital preservation mode. Edge is insufficient."
    }
