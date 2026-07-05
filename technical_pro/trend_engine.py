from technical_pro.indicators import ema, ema_slope, average_true_range

EMA_PERIODS = [9, 20, 50, 100, 200]

def clamp(value, low=0, high=100):
    return max(low, min(high, value))

def calculate_ema_stack(closes):
    return {f"ema{period}": ema(closes, period) for period in EMA_PERIODS}

def classify_ema_alignment(emas):
    values = [emas.get(f"ema{p}") for p in EMA_PERIODS]
    if any(v is None for v in values):
        return {"alignment": "Insufficient Data", "alignment_score": 50}

    bull = values[0] > values[1] > values[2] > values[3] > values[4]
    bear = values[0] < values[1] < values[2] < values[3] < values[4]

    partial_bull = sum(1 for i in range(len(values) - 1) if values[i] > values[i + 1])
    partial_bear = sum(1 for i in range(len(values) - 1) if values[i] < values[i + 1])

    if bull:
        return {"alignment": "Perfect Bull Alignment", "alignment_score": 100}
    if bear:
        return {"alignment": "Perfect Bear Alignment", "alignment_score": 0}

    score = 50 + (partial_bull - partial_bear) * 12.5
    label = "Bullish EMA Alignment" if score >= 70 else "Bearish EMA Alignment" if score <= 30 else "Mixed EMA Alignment"
    return {"alignment": label, "alignment_score": round(clamp(score), 2)}

def detect_market_structure(candles, lookback=8):
    if len(candles) < lookback * 2:
        return {"structure": "Insufficient Data", "structure_score": 50, "last_swing_high": None, "last_swing_low": None}

    recent = candles[-lookback:]
    previous = candles[-lookback * 2:-lookback]

    recent_high = max(c["high"] for c in recent)
    recent_low = min(c["low"] for c in recent)
    previous_high = max(c["high"] for c in previous)
    previous_low = min(c["low"] for c in previous)

    if recent_high > previous_high and recent_low > previous_low:
        structure = "Higher High / Higher Low"
        score = 78
    elif recent_high < previous_high and recent_low < previous_low:
        structure = "Lower High / Lower Low"
        score = 22
    elif recent_high > previous_high and recent_low < previous_low:
        structure = "Expansion / Volatile"
        score = 55
    else:
        structure = "Range / Compression"
        score = 50

    return {"structure": structure, "structure_score": score, "last_swing_high": recent_high, "last_swing_low": recent_low, "previous_high": previous_high, "previous_low": previous_low}

def detect_trend_stage(close, emas, structure):
    ema20 = emas.get("ema20")
    ema50 = emas.get("ema50")
    ema200 = emas.get("ema200")
    if ema20 is None or ema50 is None or ema200 is None:
        return {"stage": "Unknown", "stage_description": "Insufficient data"}
    if close > ema20 > ema50 > ema200 and "Higher High" in structure:
        return {"stage": "Stage 2", "stage_description": "Healthy bullish trend"}
    if close < ema20 < ema50 < ema200 and "Lower High" in structure:
        return {"stage": "Stage 4", "stage_description": "Healthy bearish trend"}
    if abs(close - ema50) / close < 0.003:
        return {"stage": "Stage 1", "stage_description": "Base / range formation"}
    return {"stage": "Transition", "stage_description": "Trend transition or pullback"}

def trend_age(closes, ema20):
    if ema20 is None:
        return None
    count = 0
    direction = closes[-1] > ema20
    for close in reversed(closes):
        if (close > ema20) == direction:
            count += 1
        else:
            break
    return count

def analyze_timeframe_trend(timeframe, candles):
    if len(candles) < 30:
        return {"timeframe": timeframe, "status": "error", "error": "Not enough candles"}

    closes = [c["close"] for c in candles]
    close = closes[-1]
    emas = calculate_ema_stack(closes)
    alignment = classify_ema_alignment(emas)
    structure = detect_market_structure(candles)
    atr = average_true_range(candles, 14)

    ema20_slope = ema_slope(closes, 20)
    ema50_slope = ema_slope(closes, 50)

    trend_score = 50
    for period in [9, 20, 50, 100, 200]:
        e = emas.get(f"ema{period}")
        if e:
            trend_score += 5 if close > e else -5

    trend_score += (alignment["alignment_score"] - 50) * 0.35
    trend_score += (structure["structure_score"] - 50) * 0.30

    if ema20_slope is not None:
        trend_score += 7 if ema20_slope > 0 else -7
    if ema50_slope is not None:
        trend_score += 5 if ema50_slope > 0 else -5

    trend_score = round(clamp(trend_score), 2)

    if trend_score >= 80:
        trend = "Strong Bull"
    elif trend_score >= 62:
        trend = "Bull"
    elif trend_score <= 20:
        trend = "Strong Bear"
    elif trend_score <= 38:
        trend = "Bear"
    else:
        trend = "Neutral"

    stage = detect_trend_stage(close, emas, structure["structure"])
    continuation_probability = round(clamp(trend_score), 2)
    pullback_probability = round(clamp(100 - trend_score), 2)
    if trend in ["Bear", "Strong Bear"]:
        continuation_probability = round(clamp(100 - trend_score), 2)
        pullback_probability = round(clamp(trend_score), 2)

    return {
        "timeframe": timeframe,
        "status": "ok",
        "latest_close": close,
        "emas": emas,
        "ema_alignment": alignment["alignment"],
        "ema_alignment_score": alignment["alignment_score"],
        "structure": structure,
        "atr14": atr,
        "ema20_slope": ema20_slope,
        "ema50_slope": ema50_slope,
        "trend": trend,
        "trend_score": trend_score,
        "trend_age": trend_age(closes, emas.get("ema20")),
        "trend_stage": stage["stage"],
        "trend_stage_description": stage["stage_description"],
        "continuation_probability": continuation_probability,
        "pullback_probability": pullback_probability
    }

def calculate_consensus(timeframe_results):
    valid = [r for r in timeframe_results.values() if r.get("status") == "ok"]
    if not valid:
        return {"overall_trend": "Unknown", "trend_consensus": 0, "average_trend_score": 0, "aligned_timeframes": 0, "total_timeframes": 0}

    avg_score = round(sum(r["trend_score"] for r in valid) / len(valid), 2)
    bullish = [r for r in valid if r["trend"] in ["Bull", "Strong Bull"]]
    bearish = [r for r in valid if r["trend"] in ["Bear", "Strong Bear"]]
    neutral = [r for r in valid if r["trend"] == "Neutral"]

    if len(bullish) > len(bearish) and len(bullish) >= len(neutral):
        overall = "Bullish"
        aligned = len(bullish)
    elif len(bearish) > len(bullish) and len(bearish) >= len(neutral):
        overall = "Bearish"
        aligned = len(bearish)
    else:
        overall = "Neutral"
        aligned = len(neutral)

    consensus = round((aligned / len(valid)) * 100, 2)
    return {"overall_trend": overall, "trend_consensus": consensus, "average_trend_score": avg_score, "aligned_timeframes": aligned, "total_timeframes": len(valid)}

def build_trend_commentary(underlying, consensus, results):
    overall = consensus["overall_trend"]
    avg = consensus["average_trend_score"]
    aligned = consensus["aligned_timeframes"]
    total = consensus["total_timeframes"]

    text = [
        f"{underlying} trend intelligence shows {overall} bias with average trend score {avg}/100.",
        f"{aligned} out of {total} timeframes are aligned with the dominant trend."
    ]
    if overall == "Bullish":
        text.append("Pullbacks are more likely to be bought while higher timeframe alignment remains intact.")
    elif overall == "Bearish":
        text.append("Rallies are more likely to be sold while bearish alignment remains intact.")
    else:
        text.append("Trend structure is mixed; avoid forcing directional trades until alignment improves.")
    return " ".join(text)
