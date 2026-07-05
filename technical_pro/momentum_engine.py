from technical_pro.indicators import rsi, rsi_series, macd_full

def clamp(value, low=0, high=100):
    return max(low, min(high, value))

def classify_rsi_regime(rsi_value):
    if rsi_value is None:
        return {"regime": "Insufficient Data", "score": 50}

    if rsi_value >= 70:
        return {"regime": "Overbought / Strong Momentum", "score": 75}
    if rsi_value >= 60:
        return {"regime": "Bullish Momentum", "score": 82}
    if rsi_value >= 52:
        return {"regime": "Mild Bullish Momentum", "score": 65}
    if rsi_value >= 48:
        return {"regime": "Neutral Momentum", "score": 50}
    if rsi_value >= 40:
        return {"regime": "Mild Bearish Momentum", "score": 35}
    if rsi_value >= 30:
        return {"regime": "Bearish Momentum", "score": 18}
    return {"regime": "Oversold / Strong Bearish Momentum", "score": 25}

def detect_rsi_slope(closes, lookback=5):
    rsis = rsi_series(closes, 14)
    if len(rsis) < lookback + 1:
        return {"slope": None, "direction": "Unknown", "score_adjustment": 0}

    slope = rsis[-1] - rsis[-lookback]
    if slope > 5:
        direction = "Accelerating Bullish"
        adj = 10
    elif slope > 1:
        direction = "Improving"
        adj = 5
    elif slope < -5:
        direction = "Accelerating Bearish"
        adj = -10
    elif slope < -1:
        direction = "Weakening"
        adj = -5
    else:
        direction = "Flat"
        adj = 0

    return {"slope": round(slope, 2), "direction": direction, "score_adjustment": adj}

def classify_macd(macd_data):
    macd = macd_data.get("macd")
    signal = macd_data.get("signal")
    hist = macd_data.get("histogram")
    slope = macd_data.get("histogram_slope")
    accel = macd_data.get("histogram_acceleration")

    if macd is None or signal is None or hist is None:
        return {"regime": "Insufficient Data", "score": 50}

    score = 50

    if macd > signal:
        score += 15
    else:
        score -= 15

    if hist > 0:
        score += 15
    else:
        score -= 15

    if slope is not None:
        if slope > 0:
            score += 10
        elif slope < 0:
            score -= 10

    if accel is not None:
        if accel > 0:
            score += 5
        elif accel < 0:
            score -= 5

    score = clamp(score)

    if score >= 75:
        regime = "Bullish MACD Expansion"
    elif score >= 60:
        regime = "Bullish MACD"
    elif score <= 25:
        regime = "Bearish MACD Expansion"
    elif score <= 40:
        regime = "Bearish MACD"
    else:
        regime = "Neutral MACD"

    return {"regime": regime, "score": round(score, 2)}

def detect_momentum_divergence(candles, closes, lookback=12):
    rsis = rsi_series(closes, 14)
    if len(candles) < lookback + 1 or len(rsis) < lookback + 1:
        return {"divergence": "Insufficient Data", "score_adjustment": 0}

    recent = candles[-lookback:]
    previous = candles[-lookback*2:-lookback] if len(candles) >= lookback * 2 else candles[:-lookback]

    if not previous:
        return {"divergence": "None", "score_adjustment": 0}

    recent_high = max(c["high"] for c in recent)
    previous_high = max(c["high"] for c in previous)
    recent_low = min(c["low"] for c in recent)
    previous_low = min(c["low"] for c in previous)

    recent_rsi = rsis[-1]
    previous_rsi = rsis[-lookback]

    if recent_high > previous_high and recent_rsi < previous_rsi:
        return {"divergence": "Bearish RSI Divergence", "score_adjustment": -12}

    if recent_low < previous_low and recent_rsi > previous_rsi:
        return {"divergence": "Bullish RSI Divergence", "score_adjustment": 12}

    return {"divergence": "None", "score_adjustment": 0}

def analyze_timeframe_momentum(timeframe, candles):
    if len(candles) < 35:
        return {"timeframe": timeframe, "status": "error", "error": "Not enough candles"}

    closes = [c["close"] for c in candles]

    rsi_value = rsi(closes, 14)
    rsi_regime = classify_rsi_regime(rsi_value)
    rsi_slope = detect_rsi_slope(closes)
    macd_data = macd_full(closes)
    macd_regime = classify_macd(macd_data)
    divergence = detect_momentum_divergence(candles, closes)

    score = (
        rsi_regime["score"] * 0.35 +
        macd_regime["score"] * 0.45 +
        50 * 0.20
    )

    score += rsi_slope["score_adjustment"]
    score += divergence["score_adjustment"]
    score = round(clamp(score), 2)

    if score >= 78:
        momentum = "Strong Bullish"
    elif score >= 62:
        momentum = "Bullish"
    elif score <= 22:
        momentum = "Strong Bearish"
    elif score <= 38:
        momentum = "Bearish"
    else:
        momentum = "Neutral"

    return {
        "timeframe": timeframe,
        "status": "ok",
        "rsi14": rsi_value,
        "rsi_regime": rsi_regime["regime"],
        "rsi_score": rsi_regime["score"],
        "rsi_slope": rsi_slope,
        "macd": macd_data,
        "macd_regime": macd_regime["regime"],
        "macd_score": macd_regime["score"],
        "divergence": divergence["divergence"],
        "momentum": momentum,
        "momentum_score": score,
        "momentum_acceleration": macd_data.get("histogram_acceleration"),
        "histogram_slope": macd_data.get("histogram_slope")
    }

def calculate_momentum_consensus(momentum_results):
    valid = [r for r in momentum_results.values() if r.get("status") == "ok"]
    if not valid:
        return {"overall_momentum": "Unknown", "momentum_consensus": 0, "average_momentum_score": 0, "aligned_timeframes": 0, "total_timeframes": 0}

    avg_score = round(sum(r["momentum_score"] for r in valid) / len(valid), 2)

    bullish = [r for r in valid if r["momentum"] in ["Bullish", "Strong Bullish"]]
    bearish = [r for r in valid if r["momentum"] in ["Bearish", "Strong Bearish"]]
    neutral = [r for r in valid if r["momentum"] == "Neutral"]

    if len(bullish) > len(bearish) and len(bullish) >= len(neutral):
        overall = "Bullish"
        aligned = len(bullish)
    elif len(bearish) > len(bullish) and len(bearish) >= len(neutral):
        overall = "Bearish"
        aligned = len(bearish)
    else:
        overall = "Neutral"
        aligned = len(neutral)

    return {
        "overall_momentum": overall,
        "momentum_consensus": round((aligned / len(valid)) * 100, 2),
        "average_momentum_score": avg_score,
        "aligned_timeframes": aligned,
        "total_timeframes": len(valid)
    }

def build_momentum_commentary(underlying, consensus, results):
    overall = consensus["overall_momentum"]
    avg = consensus["average_momentum_score"]
    aligned = consensus["aligned_timeframes"]
    total = consensus["total_timeframes"]

    text = [
        f"{underlying} momentum intelligence shows {overall} momentum with average momentum score {avg}/100.",
        f"{aligned} out of {total} timeframes agree with the dominant momentum condition."
    ]

    valid = [r for r in results.values() if r.get("status") == "ok"]
    if valid:
        strongest = max(valid, key=lambda x: abs(x["momentum_score"] - 50))
        text.append(
            f"Strongest momentum signal is on {strongest['timeframe']} with {strongest['momentum']} reading, RSI {strongest['rsi14']}, and MACD regime {strongest['macd_regime']}."
        )

    if overall == "Bullish":
        text.append("Momentum supports buy-on-dip or bullish spread structures if trend and option-chain also confirm.")
    elif overall == "Bearish":
        text.append("Momentum supports sell-on-rise or bearish spread structures if trend and option-chain also confirm.")
    else:
        text.append("Momentum is mixed; directional trades should be avoided unless higher-timeframe trend strengthens.")

    return " ".join(text)
