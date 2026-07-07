from position.position_parser import parse_position_symbol

def technical_confirmation(position):
    parsed = parse_position_symbol(position.get("tradingsymbol"))
    underlying = parsed.get("underlying")

    try:
        from technical_pro.service import get_technical_intelligence_snapshot
        tech = get_technical_intelligence_snapshot(underlying, timeframes=["day", "75m", "15m", "5m"])
    except Exception:
        tech = {"technical_score": 50, "technical_bias": "Neutral"}

    score = tech.get("technical_score", 50)
    bias = tech.get("technical_bias", "Neutral")
    pos_type = position.get("position_type")

    if pos_type == "OPTION_CALL":
        aligned = bias == "Bullish"
    elif pos_type == "OPTION_PUT":
        aligned = bias == "Bearish"
    else:
        aligned = score >= 55

    return {"technical_score": score, "technical_bias": bias, "aligned": aligned}
