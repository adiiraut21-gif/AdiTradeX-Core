def detect_structure(candles, lookback=8):
    if len(candles) < lookback + 2:
        return {
            "structure": "Insufficient Data",
            "last_swing_high": None,
            "last_swing_low": None
        }

    recent = candles[-lookback:]
    previous = candles[-(lookback*2):-lookback]

    recent_high = max(c["high"] for c in recent)
    recent_low = min(c["low"] for c in recent)
    prev_high = max(c["high"] for c in previous) if previous else None
    prev_low = min(c["low"] for c in previous) if previous else None

    if prev_high is None or prev_low is None:
        structure = "Neutral"
    elif recent_high > prev_high and recent_low > prev_low:
        structure = "Higher High / Higher Low"
    elif recent_high < prev_high and recent_low < prev_low:
        structure = "Lower High / Lower Low"
    elif recent_high > prev_high and recent_low < prev_low:
        structure = "Expansion / Volatile"
    else:
        structure = "Range / Compression"

    return {
        "structure": structure,
        "last_swing_high": recent_high,
        "last_swing_low": recent_low,
        "previous_high": prev_high,
        "previous_low": prev_low
    }
