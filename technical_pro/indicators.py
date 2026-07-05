def ema_series(values, period):
    if not values:
        return []
    k = 2 / (period + 1)
    ema = values[0]
    out = []
    for value in values:
        ema = (value * k) + (ema * (1 - k))
        out.append(ema)
    return out

def ema(values, period):
    series = ema_series(values, period)
    if len(series) < period:
        return None
    return round(series[-1], 2)

def ema_slope(values, period, lookback=5):
    series = ema_series(values, period)
    if len(series) < period + lookback:
        return None
    return round(series[-1] - series[-lookback], 2)

def rsi_series(values, period=14):
    if len(values) <= period:
        return []

    gains = []
    losses = []
    for i in range(1, len(values)):
        change = values[i] - values[i - 1]
        gains.append(max(change, 0))
        losses.append(abs(min(change, 0)))

    rsis = []
    for i in range(period, len(gains) + 1):
        avg_gain = sum(gains[i-period:i]) / period
        avg_loss = sum(losses[i-period:i]) / period
        if avg_loss == 0:
            rsis.append(100)
        else:
            rs = avg_gain / avg_loss
            rsis.append(100 - (100 / (1 + rs)))

    return rsis

def rsi(values, period=14):
    series = rsi_series(values, period)
    if not series:
        return None
    return round(series[-1], 2)

def macd_full(values, fast=12, slow=26, signal=9):
    if len(values) < slow + signal:
        return {"macd": None, "signal": None, "histogram": None, "histogram_slope": None, "histogram_acceleration": None}

    fast_series = ema_series(values, fast)
    slow_series = ema_series(values, slow)
    macd_line = [f - s for f, s in zip(fast_series, slow_series)]
    signal_line = ema_series(macd_line, signal)
    hist_series = [m - s for m, s in zip(macd_line, signal_line)]

    hist = hist_series[-1]
    prev_hist = hist_series[-2] if len(hist_series) >= 2 else hist
    prev2_hist = hist_series[-3] if len(hist_series) >= 3 else prev_hist

    slope = hist - prev_hist
    prev_slope = prev_hist - prev2_hist
    accel = slope - prev_slope

    return {
        "macd": round(macd_line[-1], 2),
        "signal": round(signal_line[-1], 2),
        "histogram": round(hist, 2),
        "histogram_slope": round(slope, 2),
        "histogram_acceleration": round(accel, 2)
    }

def average_true_range(candles, period=14):
    if len(candles) < period + 1:
        return None
    trs = []
    for i, candle in enumerate(candles):
        if i == 0:
            trs.append(candle["high"] - candle["low"])
        else:
            previous_close = candles[i - 1]["close"]
            trs.append(max(
                candle["high"] - candle["low"],
                abs(candle["high"] - previous_close),
                abs(candle["low"] - previous_close)
            ))
    return round(sum(trs[-period:]) / period, 2)
