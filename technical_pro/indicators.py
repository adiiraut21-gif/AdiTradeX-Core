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
