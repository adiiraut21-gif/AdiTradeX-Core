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
        return {"structure": "Higher High / Higher Low", "structure_score": 78, "last_swing_high": recent_high, "last_swing_low": recent_low, "previous_high": previous_high, "previous_low": previous_low}
    if recent_high < previous_high and recent_low < previous_low:
        return {"structure": "Lower High / Lower Low", "structure_score": 22, "last_swing_high": recent_high, "last_swing_low": recent_low, "previous_high": previous_high, "previous_low": previous_low}
    if recent_high > previous_high and recent_low < previous_low:
        return {"structure": "Expansion / Volatile", "structure_score": 55, "last_swing_high": recent_high, "last_swing_low": recent_low, "previous_high": previous_high, "previous_low": previous_low}
    return {"structure": "Range / Compression", "structure_score": 50, "last_swing_high": recent_high, "last_swing_low": recent_low, "previous_high": previous_high, "previous_low": previous_low}

def analyze_timeframe_trend(timeframe, candles):
    if len(candles) < 30:
        return {"timeframe": timeframe, "status": "error", "error": "Not enough candles"}
    closes = [c["close"] for c in candles]
    close = closes[-1]
    emas = calculate_ema_stack(closes)
    alignment = classify_ema_alignment(emas)
    structure = detect_market_structure(candles)
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
    trend = "Strong Bull" if trend_score >= 80 else "Bull" if trend_score >= 62 else "Strong Bear" if trend_score <= 20 else "Bear" if trend_score <= 38 else "Neutral"
    return {
        "timeframe": timeframe, "status": "ok", "latest_close": close, "emas": emas,
        "ema_alignment": alignment["alignment"], "ema_alignment_score": alignment["alignment_score"],
        "structure": structure, "atr14": average_true_range(candles, 14),
        "ema20_slope": ema20_slope, "ema50_slope": ema50_slope,
        "trend": trend, "trend_score": trend_score,
        "trend_stage": "Stage 2" if trend in ["Bull","Strong Bull"] else "Stage 4" if trend in ["Bear","Strong Bear"] else "Transition",
        "continuation_probability": round(clamp(trend_score if trend in ["Bull","Strong Bull"] else 100 - trend_score if trend in ["Bear","Strong Bear"] else 50), 2),
        "pullback_probability": round(clamp(100 - trend_score if trend in ["Bull","Strong Bull"] else trend_score if trend in ["Bear","Strong Bear"] else 50), 2)
    }

def calculate_consensus(results):
    valid = [r for r in results.values() if r.get("status") == "ok"]
    if not valid:
        return {"overall_trend": "Unknown", "trend_consensus": 0, "average_trend_score": 0, "aligned_timeframes": 0, "total_timeframes": 0}
    avg = round(sum(r["trend_score"] for r in valid) / len(valid), 2)
    bull = [r for r in valid if r["trend"] in ["Bull", "Strong Bull"]]
    bear = [r for r in valid if r["trend"] in ["Bear", "Strong Bear"]]
    neutral = [r for r in valid if r["trend"] == "Neutral"]
    if len(bull) > len(bear) and len(bull) >= len(neutral):
        overall, aligned = "Bullish", len(bull)
    elif len(bear) > len(bull) and len(bear) >= len(neutral):
        overall, aligned = "Bearish", len(bear)
    else:
        overall, aligned = "Neutral", len(neutral)
    return {"overall_trend": overall, "trend_consensus": round((aligned/len(valid))*100,2), "average_trend_score": avg, "aligned_timeframes": aligned, "total_timeframes": len(valid)}

def build_trend_commentary(underlying, consensus, results):
    return f"{underlying} trend intelligence shows {consensus['overall_trend']} bias with average trend score {consensus['average_trend_score']}/100. {consensus['aligned_timeframes']} out of {consensus['total_timeframes']} timeframes are aligned."
