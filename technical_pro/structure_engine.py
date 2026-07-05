def clamp(value, low=0, high=100):
    return max(low, min(high, value))

def swing_points(candles, window=3):
    highs = []
    lows = []
    if len(candles) < window * 2 + 1:
        return highs, lows

    for i in range(window, len(candles) - window):
        mid = candles[i]
        left = candles[i-window:i]
        right = candles[i+1:i+window+1]

        if all(mid["high"] > c["high"] for c in left + right):
            highs.append({"index": i, "time": mid["time"], "price": mid["high"]})

        if all(mid["low"] < c["low"] for c in left + right):
            lows.append({"index": i, "time": mid["time"], "price": mid["low"]})

    return highs[-5:], lows[-5:]

def detect_bos_choch(candles):
    highs, lows = swing_points(candles)
    close = candles[-1]["close"]

    if not highs or not lows:
        return {"event": "Insufficient Structure", "score_adjustment": 0}

    last_high = highs[-1]["price"]
    last_low = lows[-1]["price"]

    if close > last_high:
        return {"event": "Bullish Break of Structure", "score_adjustment": 15, "level": last_high}

    if close < last_low:
        return {"event": "Bearish Break of Structure", "score_adjustment": -15, "level": last_low}

    return {"event": "No Break of Structure", "score_adjustment": 0, "level": None}

def detect_liquidity_sweep(candles, lookback=10):
    if len(candles) < lookback + 2:
        return {"sweep": "Insufficient Data", "score_adjustment": 0}

    previous = candles[-lookback-1:-1]
    current = candles[-1]
    prev_high = max(c["high"] for c in previous)
    prev_low = min(c["low"] for c in previous)

    if current["high"] > prev_high and current["close"] < prev_high:
        return {"sweep": "Bearish Liquidity Sweep", "score_adjustment": -12, "level": prev_high}

    if current["low"] < prev_low and current["close"] > prev_low:
        return {"sweep": "Bullish Liquidity Sweep", "score_adjustment": 12, "level": prev_low}

    return {"sweep": "None", "score_adjustment": 0, "level": None}

def detect_compression_expansion(candles, lookback=10):
    if len(candles) < lookback * 2:
        return {"state": "Insufficient Data", "score_adjustment": 0}

    recent = candles[-lookback:]
    previous = candles[-lookback*2:-lookback]
    recent_range = max(c["high"] for c in recent) - min(c["low"] for c in recent)
    previous_range = max(c["high"] for c in previous) - min(c["low"] for c in previous)

    if previous_range == 0:
        return {"state": "Unknown", "score_adjustment": 0}

    ratio = recent_range / previous_range

    if ratio > 1.35:
        return {"state": "Expansion", "score_adjustment": 7, "range_ratio": round(ratio, 2)}
    if ratio < 0.70:
        return {"state": "Compression", "score_adjustment": -3, "range_ratio": round(ratio, 2)}
    return {"state": "Normal", "score_adjustment": 0, "range_ratio": round(ratio, 2)}

def analyze_timeframe_structure(timeframe, candles):
    if len(candles) < 25:
        return {"timeframe": timeframe, "status": "error", "error": "Not enough candles"}

    highs, lows = swing_points(candles)
    bos = detect_bos_choch(candles)
    sweep = detect_liquidity_sweep(candles)
    compression = detect_compression_expansion(candles)

    score = 50
    score += bos.get("score_adjustment", 0)
    score += sweep.get("score_adjustment", 0)
    score += compression.get("score_adjustment", 0)

    if len(highs) >= 2 and highs[-1]["price"] > highs[-2]["price"]:
        score += 8
    if len(lows) >= 2 and lows[-1]["price"] > lows[-2]["price"]:
        score += 8
    if len(highs) >= 2 and highs[-1]["price"] < highs[-2]["price"]:
        score -= 8
    if len(lows) >= 2 and lows[-1]["price"] < lows[-2]["price"]:
        score -= 8

    score = round(clamp(score), 2)

    if score >= 70:
        bias = "Bullish Structure"
    elif score <= 30:
        bias = "Bearish Structure"
    else:
        bias = "Neutral Structure"

    return {
        "timeframe": timeframe,
        "status": "ok",
        "structure_bias": bias,
        "structure_score": score,
        "swing_highs": highs,
        "swing_lows": lows,
        "bos_choch": bos,
        "liquidity_sweep": sweep,
        "compression_expansion": compression
    }

def calculate_structure_consensus(results):
    valid = [r for r in results.values() if r.get("status") == "ok"]
    if not valid:
        return {"overall_structure": "Unknown", "structure_consensus": 0, "average_structure_score": 0, "aligned_timeframes": 0, "total_timeframes": 0}

    avg = round(sum(r["structure_score"] for r in valid) / len(valid), 2)
    bull = [r for r in valid if r["structure_bias"] == "Bullish Structure"]
    bear = [r for r in valid if r["structure_bias"] == "Bearish Structure"]
    neutral = [r for r in valid if r["structure_bias"] == "Neutral Structure"]

    if len(bull) > len(bear) and len(bull) >= len(neutral):
        overall, aligned = "Bullish", len(bull)
    elif len(bear) > len(bull) and len(bear) >= len(neutral):
        overall, aligned = "Bearish", len(bear)
    else:
        overall, aligned = "Neutral", len(neutral)

    return {"overall_structure": overall, "structure_consensus": round((aligned/len(valid))*100,2), "average_structure_score": avg, "aligned_timeframes": aligned, "total_timeframes": len(valid)}
