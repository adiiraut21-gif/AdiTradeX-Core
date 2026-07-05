def sma(values, period):
    if len(values) < period:
        return None
    return sum(values[-period:]) / period

def ema_series(values, period):
    if not values:
        return []
    k = 2 / (period + 1)
    out = []
    ema = values[0]
    for v in values:
        ema = (v * k) + (ema * (1 - k))
        out.append(ema)
    return out

def ema(values, period):
    series = ema_series(values, period)
    return round(series[-1], 2) if len(series) >= period else None

def rsi(values, period=14):
    if len(values) <= period:
        return None

    gains = []
    losses = []
    for i in range(1, len(values)):
        change = values[i] - values[i-1]
        gains.append(max(change, 0))
        losses.append(abs(min(change, 0)))

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)

def macd(values, fast=12, slow=26, signal=9):
    if len(values) < slow + signal:
        return {"macd": None, "signal": None, "histogram": None}

    fast_series = ema_series(values, fast)
    slow_series = ema_series(values, slow)

    macd_line = [f - s for f, s in zip(fast_series, slow_series)]
    signal_line = ema_series(macd_line, signal)
    hist = macd_line[-1] - signal_line[-1]

    return {
        "macd": round(macd_line[-1], 2),
        "signal": round(signal_line[-1], 2),
        "histogram": round(hist, 2)
    }

def true_ranges(candles):
    trs = []
    for i, c in enumerate(candles):
        high = c["high"]
        low = c["low"]
        if i == 0:
            trs.append(high - low)
        else:
            prev_close = candles[i-1]["close"]
            trs.append(max(high - low, abs(high - prev_close), abs(low - prev_close)))
    return trs

def atr(candles, period=14):
    if len(candles) < period:
        return None
    trs = true_ranges(candles)
    return round(sum(trs[-period:]) / period, 2)

def bollinger(values, period=20, mult=2):
    if len(values) < period:
        return {"upper": None, "middle": None, "lower": None}
    subset = values[-period:]
    middle = sum(subset) / period
    variance = sum((x - middle) ** 2 for x in subset) / period
    sd = variance ** 0.5
    return {
        "upper": round(middle + mult * sd, 2),
        "middle": round(middle, 2),
        "lower": round(middle - mult * sd, 2)
    }

def vwap(candles):
    pv = 0
    vol = 0
    for c in candles:
        volume = c.get("volume") or 0
        typical = (c["high"] + c["low"] + c["close"]) / 3
        pv += typical * volume
        vol += volume
    if vol == 0:
        return None
    return round(pv / vol, 2)
