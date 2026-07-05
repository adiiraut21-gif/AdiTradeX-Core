def clamp(x, low=0, high=100):
    return max(low, min(high, x))

def trend_score(close, ema9, ema20, ema50, ema200):
    score = 50
    if ema9 and close > ema9:
        score += 10
    if ema20 and close > ema20:
        score += 10
    if ema50 and close > ema50:
        score += 10
    if ema200 and close > ema200:
        score += 10
    if ema9 and ema20 and ema9 > ema20:
        score += 10
    if ema20 and ema50 and ema20 > ema50:
        score += 10
    return clamp(score)

def momentum_score(rsi_value, macd_data):
    score = 50
    if rsi_value:
        if rsi_value > 60:
            score += 20
        elif rsi_value > 50:
            score += 10
        elif rsi_value < 40:
            score -= 20
        elif rsi_value < 50:
            score -= 10

    hist = macd_data.get("histogram")
    if hist is not None:
        if hist > 0:
            score += 15
        elif hist < 0:
            score -= 15

    return clamp(score)

def volatility_score(close, atr_value):
    if not close or not atr_value:
        return 50
    atr_pct = (atr_value / close) * 100
    if atr_pct < 0.4:
        return 45
    if atr_pct < 0.9:
        return 70
    if atr_pct < 1.5:
        return 60
    return 40

def structure_score(structure):
    s = structure.lower()
    if "higher high" in s:
        return 75
    if "lower high" in s:
        return 25
    if "range" in s:
        return 50
    if "expansion" in s:
        return 55
    return 50

def bias_from_score(score):
    if score >= 65:
        return "Bullish"
    if score <= 40:
        return "Bearish"
    return "Neutral"

def grade(score):
    if score >= 85:
        return "A+"
    if score >= 75:
        return "A"
    if score >= 65:
        return "B"
    if score >= 50:
        return "C"
    return "D"
