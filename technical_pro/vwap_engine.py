def clamp(value, low=0, high=100):
    return max(low, min(high, value))

def calc_vwap(candles):
    pv = 0
    vol = 0

    for c in candles:
        v = c.get("volume") or 0
        typical = (c["high"] + c["low"] + c["close"]) / 3
        pv += typical * v
        vol += v

    if vol == 0:
        return None

    return round(pv / vol, 2)

def vwap_slope(candles, lookback=5):
    if len(candles) < lookback * 2:
        return None

    current = calc_vwap(candles[-lookback:])
    previous = calc_vwap(candles[-lookback*2:-lookback])

    if current is None or previous is None:
        return None

    return round(current - previous, 2)

def vwap_bands(candles, vwap):
    if not candles or vwap is None:
        return None

    closes = [c["close"] for c in candles[-30:]]
    if not closes:
        return None

    variance = sum((c - vwap) ** 2 for c in closes) / len(closes)
    sd = variance ** 0.5

    return {
        "upper_1sd": round(vwap + sd, 2),
        "lower_1sd": round(vwap - sd, 2),
        "upper_2sd": round(vwap + 2 * sd, 2),
        "lower_2sd": round(vwap - 2 * sd, 2)
    }

def analyze_timeframe_vwap(timeframe, candles, source="spot"):
    if len(candles) < 10:
        return {"timeframe": timeframe, "status": "error", "error": "Not enough candles"}

    vwap = calc_vwap(candles)
    close = candles[-1]["close"]
    slope = vwap_slope(candles)

    if vwap is None:
        return {
            "timeframe": timeframe,
            "status": "error",
            "error": "Volume unavailable for VWAP",
            "vwap_source": source
        }

    distance = round(close - vwap, 2)
    distance_pct = round((distance / close) * 100, 2)

    score = 50

    if close > vwap:
        score += 18
        zone = "Premium Zone"
    elif close < vwap:
        score -= 18
        zone = "Discount Zone"
    else:
        zone = "Fair Value"

    if slope is not None:
        if slope > 0:
            score += 12
        elif slope < 0:
            score -= 12

    if abs(distance_pct) < 0.10:
        acceptance = "VWAP Acceptance"
    elif close > vwap and slope and slope > 0:
        acceptance = "Bullish VWAP Acceptance"
        score += 8
    elif close < vwap and slope and slope < 0:
        acceptance = "Bearish VWAP Acceptance"
        score -= 8
    else:
        acceptance = "VWAP Rejection / Transition"

    score = round(clamp(score), 2)

    if score >= 70:
        bias = "Bullish VWAP"
    elif score <= 30:
        bias = "Bearish VWAP"
    else:
        bias = "Neutral VWAP"

    bands = vwap_bands(candles, vwap)

    return {
        "timeframe": timeframe,
        "status": "ok",
        "vwap_source": source,
        "vwap": vwap,
        "close": close,
        "distance": distance,
        "distance_pct": distance_pct,
        "vwap_slope": slope,
        "zone": zone,
        "acceptance": acceptance,
        "vwap_bias": bias,
        "vwap_score": score,
        "vwap_bands": bands
    }

def calculate_vwap_consensus(results):
    valid = [r for r in results.values() if r.get("status") == "ok"]

    if not valid:
        return {
            "overall_vwap": "Unknown",
            "vwap_consensus": 0,
            "average_vwap_score": 0,
            "aligned_timeframes": 0,
            "total_timeframes": 0
        }

    avg = round(sum(r["vwap_score"] for r in valid) / len(valid), 2)

    bull = [r for r in valid if r["vwap_bias"] == "Bullish VWAP"]
    bear = [r for r in valid if r["vwap_bias"] == "Bearish VWAP"]
    neutral = [r for r in valid if r["vwap_bias"] == "Neutral VWAP"]

    if len(bull) > len(bear) and len(bull) >= len(neutral):
        overall, aligned = "Bullish", len(bull)
    elif len(bear) > len(bull) and len(bear) >= len(neutral):
        overall, aligned = "Bearish", len(bear)
    else:
        overall, aligned = "Neutral", len(neutral)

    return {
        "overall_vwap": overall,
        "vwap_consensus": round((aligned / len(valid)) * 100, 2),
        "average_vwap_score": avg,
        "aligned_timeframes": aligned,
        "total_timeframes": len(valid)
    }
