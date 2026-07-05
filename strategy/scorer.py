def clamp(value, low=0, high=100):
    return max(low, min(high, value))

def score_strategy(strategy, analytics, technical):
    name = strategy["name"]

    bull = analytics.get("bull_score", 50)
    bear = analytics.get("bear_score", 50)
    trade_quality = analytics.get("trade_quality", 50)
    range_probability = analytics.get("range_probability", 50)
    institutional_bias = analytics.get("institutional_bias", "Neutral")

    technical_score = technical.get("scores", {}).get("technical_score", 50)
    technical_bias = technical.get("technical_bias", "Neutral")

    base = (trade_quality * 0.35) + (technical_score * 0.35)

    if name == "Long Call":
        score = base + (bull * 0.25) - (range_probability * 0.10)
        reason = "Directional CE works only when option-chain and technical momentum both support expansion."
    elif name == "Long Put":
        score = base + (bear * 0.25) - (range_probability * 0.10)
        reason = "Directional PE works only when downside momentum is strong and range risk is low."
    elif name == "Bull Call Spread":
        score = base + (bull * 0.25) + 8
        reason = "Bull Call Spread lowers cost and theta risk versus naked CE."
    elif name == "Bear Put Spread":
        score = base + (bear * 0.25) + 8
        reason = "Bear Put Spread lowers cost and theta risk versus naked PE."
    elif name == "Bull Put Credit Spread":
        score = base + (bull * 0.18) + (range_probability * 0.22)
        reason = "Bull Put Credit Spread benefits when support is expected to hold."
    elif name == "Bear Call Credit Spread":
        score = base + (bear * 0.18) + (range_probability * 0.22)
        reason = "Bear Call Credit Spread benefits when resistance is expected to hold."
    else:
        score = 40
        reason = "Fallback strategy."

    # Bias alignment bonuses / penalties
    if "Bull" in name or name == "Long Call":
        if institutional_bias == "Bullish":
            score += 6
        if technical_bias == "Bullish":
            score += 6
        if institutional_bias == "Bearish":
            score -= 15
        if technical_bias == "Bearish":
            score -= 15

    if "Bear" in name or name == "Long Put":
        if institutional_bias == "Bearish":
            score += 6
        if technical_bias == "Bearish":
            score += 6
        if institutional_bias == "Bullish":
            score -= 15
        if technical_bias == "Bullish":
            score -= 15

    if name in ["Long Call", "Long Put"] and range_probability > 60:
        score -= 12

    if "Spread" in name:
        risk_rating = "Low"
    elif name in ["Long Call", "Long Put"]:
        risk_rating = "High" if range_probability > 55 else "Medium"
    else:
        risk_rating = "Medium"

    score = round(clamp(score), 2)

    return {
        **strategy,
        "score": score,
        "ev_score": round(score / 10, 2),
        "confidence": score,
        "risk_rating": risk_rating,
        "reason": reason
    }

def no_trade_strategy(analytics, technical):
    trade_quality = analytics.get("trade_quality", 50)
    technical_score = technical.get("scores", {}).get("technical_score", 50)
    range_probability = analytics.get("range_probability", 50)

    analytics_conflict = 100 - abs(analytics.get("bull_score", 50) - analytics.get("bear_score", 50))
    score = (analytics_conflict * 0.30) + (range_probability * 0.35) + ((100 - trade_quality) * 0.20) + ((100 - technical_score) * 0.15)
    score = round(clamp(score), 2)

    return {
        "name": "No Trade",
        "type": "Capital Preservation",
        "direction": "Neutral",
        "score": score,
        "ev_score": round(score / 10, 2),
        "confidence": score,
        "risk_rating": "None",
        "reason": "Capital preservation is preferred when signals are mixed, technical score is weak, or range probability is high."
    }
