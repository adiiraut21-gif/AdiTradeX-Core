def make_position_decision(position, technical, option_chain, risk):
    tech_score = technical.get("technical_score", 50)
    oc_score = option_chain.get("option_chain_score", 50)
    aligned = technical.get("aligned", False)
    score = round(tech_score * 0.55 + oc_score * 0.45, 2)

    if score >= 82 and aligned:
        action = "STRONG HOLD"
    elif score >= 68 and aligned:
        action = "HOLD"
    elif score >= 55:
        action = "HOLD WITH TRAILING SL"
    elif score >= 45:
        action = "PARTIAL EXIT / REDUCE"
    else:
        action = "EXIT"

    if risk.get("pnl_pct", 0) > 35 and score < 70:
        action = "BOOK PARTIAL PROFIT"

    confidence = min(100, round(50 + abs(score - 50) * 1.4, 2))
    return {
        "action": action,
        "position_score": score,
        "confidence": confidence,
        "summary": (
            f"{position.get('tradingsymbol')} action is {action}. "
            f"Score {score}/100. Technical bias {technical.get('technical_bias')}; "
            f"option-chain bias {option_chain.get('institutional_bias')}. "
            f"SL {risk.get('stop_loss')}, T1 {risk.get('target_1')}, T2 {risk.get('target_2')}."
        )
    }
