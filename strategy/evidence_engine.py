def build_evidence(component_scores, market_regime=None, probability=None):
    positive = []
    negative = []

    def evaluate(name, score, positive_points, negative_points):
        if score >= 70:
            positive.append({
                "factor": name,
                "impact": f"+{positive_points}",
                "score": score,
                "reason": f"{name} supports the setup."
            })
        elif score <= 40:
            negative.append({
                "factor": name,
                "impact": f"-{negative_points}",
                "score": score,
                "reason": f"{name} is weak or conflicting."
            })

    evaluate("Trend Alignment", component_scores.get("trend", 50), 18, 18)
    evaluate("Momentum", component_scores.get("momentum", 50), 14, 14)
    evaluate("Market Structure", component_scores.get("structure", 50), 14, 14)
    evaluate("Futures VWAP", component_scores.get("vwap", 50), 16, 16)
    evaluate("Option Chain", component_scores.get("option_chain", 50), 12, 12)
    evaluate("Liquidity", component_scores.get("liquidity", 50), 10, 10)

    if market_regime:
        regime = market_regime.get("regime", "Neutral")
        strength = market_regime.get("regime_strength", 50)
        if regime in ["Strong Bull", "Strong Bear"] and strength >= 70:
            positive.append({
                "factor": "Market Regime",
                "impact": "+12",
                "score": strength,
                "reason": f"{regime} regime supports directional edge."
            })
        elif regime in ["Neutral", "Transition"]:
            negative.append({
                "factor": "Market Regime",
                "impact": "-8",
                "score": strength,
                "reason": f"{regime} regime reduces conviction."
            })

    if probability:
        dominant = probability.get("dominant_probability", 50)
        if dominant >= 70:
            positive.append({
                "factor": "Probability Edge",
                "impact": "+10",
                "score": dominant,
                "reason": "Dominant probability is strong."
            })
        elif dominant <= 55:
            negative.append({
                "factor": "Weak Probability Edge",
                "impact": "-10",
                "score": dominant,
                "reason": "No clear bull/bear/neutral edge."
            })

    return {
        "positive": positive,
        "negative": negative
    }
