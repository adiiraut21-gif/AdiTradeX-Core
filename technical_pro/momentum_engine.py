from technical_pro.indicators import rsi, rsi_series, macd_full

def clamp(value, low=0, high=100):
    return max(low, min(high, value))

def classify_rsi_regime(rsi_value):
    if rsi_value is None: return {"regime": "Insufficient Data", "score": 50}
    if rsi_value >= 70: return {"regime": "Overbought / Strong Momentum", "score": 75}
    if rsi_value >= 60: return {"regime": "Bullish Momentum", "score": 82}
    if rsi_value >= 52: return {"regime": "Mild Bullish Momentum", "score": 65}
    if rsi_value >= 48: return {"regime": "Neutral Momentum", "score": 50}
    if rsi_value >= 40: return {"regime": "Mild Bearish Momentum", "score": 35}
    if rsi_value >= 30: return {"regime": "Bearish Momentum", "score": 18}
    return {"regime": "Oversold / Strong Bearish Momentum", "score": 25}

def detect_rsi_slope(closes, lookback=5):
    rsis = rsi_series(closes, 14)
    if len(rsis) < lookback + 1:
        return {"slope": None, "direction": "Unknown", "score_adjustment": 0}
    slope = rsis[-1] - rsis[-lookback]
    if slope > 5: return {"slope": round(slope,2), "direction": "Accelerating Bullish", "score_adjustment": 10}
    if slope > 1: return {"slope": round(slope,2), "direction": "Improving", "score_adjustment": 5}
    if slope < -5: return {"slope": round(slope,2), "direction": "Accelerating Bearish", "score_adjustment": -10}
    if slope < -1: return {"slope": round(slope,2), "direction": "Weakening", "score_adjustment": -5}
    return {"slope": round(slope,2), "direction": "Flat", "score_adjustment": 0}

def classify_macd(macd_data):
    if macd_data.get("macd") is None:
        return {"regime": "Insufficient Data", "score": 50}
    score = 50
    score += 15 if macd_data["macd"] > macd_data["signal"] else -15
    score += 15 if macd_data["histogram"] > 0 else -15
    score += 10 if (macd_data.get("histogram_slope") or 0) > 0 else -10
    score += 5 if (macd_data.get("histogram_acceleration") or 0) > 0 else -5
    score = clamp(score)
    regime = "Bullish MACD Expansion" if score >= 75 else "Bullish MACD" if score >= 60 else "Bearish MACD Expansion" if score <= 25 else "Bearish MACD" if score <= 40 else "Neutral MACD"
    return {"regime": regime, "score": round(score,2)}

def analyze_timeframe_momentum(timeframe, candles):
    if len(candles) < 35:
        return {"timeframe": timeframe, "status": "error", "error": "Not enough candles"}
    closes = [c["close"] for c in candles]
    rsi_value = rsi(closes, 14)
    rsi_regime = classify_rsi_regime(rsi_value)
    rsi_slope = detect_rsi_slope(closes)
    macd_data = macd_full(closes)
    macd_regime = classify_macd(macd_data)
    score = rsi_regime["score"] * 0.40 + macd_regime["score"] * 0.50 + 50 * 0.10
    score += rsi_slope["score_adjustment"]
    score = round(clamp(score), 2)
    momentum = "Strong Bullish" if score >= 78 else "Bullish" if score >= 62 else "Strong Bearish" if score <= 22 else "Bearish" if score <= 38 else "Neutral"
    return {"timeframe": timeframe, "status": "ok", "rsi14": rsi_value, "rsi_regime": rsi_regime["regime"], "rsi_score": rsi_regime["score"], "rsi_slope": rsi_slope, "macd": macd_data, "macd_regime": macd_regime["regime"], "macd_score": macd_regime["score"], "divergence": "Not checked", "momentum": momentum, "momentum_score": score, "momentum_acceleration": macd_data.get("histogram_acceleration"), "histogram_slope": macd_data.get("histogram_slope")}

def calculate_momentum_consensus(results):
    valid = [r for r in results.values() if r.get("status") == "ok"]
    if not valid:
        return {"overall_momentum": "Unknown", "momentum_consensus": 0, "average_momentum_score": 0, "aligned_timeframes": 0, "total_timeframes": 0}
    avg = round(sum(r["momentum_score"] for r in valid) / len(valid), 2)
    bull = [r for r in valid if r["momentum"] in ["Bullish","Strong Bullish"]]
    bear = [r for r in valid if r["momentum"] in ["Bearish","Strong Bearish"]]
    neutral = [r for r in valid if r["momentum"] == "Neutral"]
    if len(bull) > len(bear) and len(bull) >= len(neutral):
        overall, aligned = "Bullish", len(bull)
    elif len(bear) > len(bull) and len(bear) >= len(neutral):
        overall, aligned = "Bearish", len(bear)
    else:
        overall, aligned = "Neutral", len(neutral)
    return {"overall_momentum": overall, "momentum_consensus": round((aligned/len(valid))*100,2), "average_momentum_score": avg, "aligned_timeframes": aligned, "total_timeframes": len(valid)}

def build_momentum_commentary(underlying, consensus, results):
    return f"{underlying} momentum intelligence shows {consensus['overall_momentum']} momentum with average momentum score {consensus['average_momentum_score']}/100. {consensus['aligned_timeframes']} out of {consensus['total_timeframes']} timeframes agree."
