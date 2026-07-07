from position.position_parser import parse_position_symbol

def option_chain_confirmation(position):
    parsed = parse_position_symbol(position.get("tradingsymbol"))
    underlying = parsed.get("underlying")

    try:
        from analytics.service import analyze_underlying
        analytics = analyze_underlying(underlying)
    except Exception as e:
        return {
            "status": "error",
            "option_chain_score": 50,
            "institutional_bias": "Neutral",
            "pcr": None,
            "support": None,
            "resistance": None,
            "max_pain": None,
            "reason": str(e)
        }

    pcr = analytics.get("pcr") or 1
    bias = analytics.get("institutional_bias", "Neutral")
    pos_type = position.get("position_type")
    score = 50

    if pos_type == "OPTION_CALL":
        if bias == "Bullish":
            score += 25
        if pcr >= 1:
            score += 10
        elif pcr < 0.85:
            score -= 15
    elif pos_type == "OPTION_PUT":
        if bias == "Bearish":
            score += 25
        if pcr < 0.9:
            score += 10
        elif pcr > 1.2:
            score -= 15
    else:
        if bias == "Bullish":
            score += 10
        elif bias == "Bearish":
            score -= 10

    return {
        "status": "ok",
        "option_chain_score": max(0, min(100, round(score, 2))),
        "institutional_bias": bias,
        "pcr": pcr,
        "support": analytics.get("support"),
        "resistance": analytics.get("resistance"),
        "max_pain": analytics.get("max_pain"),
        "reason": analytics.get("summary")
    }
