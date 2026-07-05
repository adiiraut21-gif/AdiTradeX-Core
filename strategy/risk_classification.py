def risk_classification(institutional_score, engine_confidence, ev_score):
    if institutional_score >= 85 and engine_confidence >= 70 and ev_score >= 75:
        return {
            "risk_level": "Low",
            "risk_action": "Eligible for strategy selection"
        }

    if institutional_score >= 75 and ev_score >= 65:
        return {
            "risk_level": "Medium",
            "risk_action": "Proceed only with defined-risk strategy"
        }

    if institutional_score >= 65:
        return {
            "risk_level": "High",
            "risk_action": "Watchlist only"
        }

    return {
        "risk_level": "Very High",
        "risk_action": "No Trade"
    }
