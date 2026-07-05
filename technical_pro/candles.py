from datetime import datetime, timedelta
from auth.session_store import get_latest_session
from auth.kite_client import get_kite_client
from technical_pro.symbols import TECHNICAL_PRO_SYMBOLS, KITE_INTERVALS, LOOKBACK_DAYS

def get_kite():
    session = get_latest_session()
    if not session:
        raise RuntimeError("Not logged in. Login with Zerodha first.")
    return get_kite_client(session["access_token"])

def normalize_candle(candle):
    return {
        "time": str(candle.get("date")),
        "open": candle.get("open"),
        "high": candle.get("high"),
        "low": candle.get("low"),
        "close": candle.get("close"),
        "volume": candle.get("volume")
    }

def fetch_raw_candles(underlying="nifty", timeframe="15m"):
    key = underlying.lower()
    if key not in TECHNICAL_PRO_SYMBOLS:
        raise RuntimeError(f"Unsupported underlying: {underlying}")

    if timeframe == "75m":
        base_candles = fetch_raw_candles(underlying, "15m")
        return resample_to_75m(base_candles)

    kite_interval = KITE_INTERVALS.get(timeframe)
    if not kite_interval:
        raise RuntimeError(f"Unsupported timeframe: {timeframe}")

    token = TECHNICAL_PRO_SYMBOLS[key]["instrument_token"]
    days = LOOKBACK_DAYS.get(timeframe, 10)

    to_date = datetime.now()
    from_date = to_date - timedelta(days=days)

    raw = get_kite().historical_data(
        instrument_token=token,
        from_date=from_date,
        to_date=to_date,
        interval=kite_interval
    )

    return [normalize_candle(c) for c in raw]

def resample_to_75m(candles):
    if not candles:
        return []
    grouped = []
    bucket = []
    for candle in candles:
        bucket.append(candle)
        if len(bucket) == 5:
            grouped.append(build_group_candle(bucket))
            bucket = []
    if bucket:
        grouped.append(build_group_candle(bucket))
    return grouped

def build_group_candle(bucket):
    return {
        "time": bucket[0]["time"],
        "open": bucket[0]["open"],
        "high": max(c["high"] for c in bucket),
        "low": min(c["low"] for c in bucket),
        "close": bucket[-1]["close"],
        "volume": sum((c.get("volume") or 0) for c in bucket)
    }

def candle_summary(candles):
    if not candles:
        return {"count": 0, "first_time": None, "last_time": None, "last_close": None, "change": None, "change_pct": None}
    first = candles[0]
    last = candles[-1]
    change = None
    change_pct = None
    if first.get("close") and last.get("close"):
        change = round(last["close"] - first["close"], 2)
        change_pct = round((change / first["close"]) * 100, 2)
    return {
        "count": len(candles),
        "first_time": first.get("time"),
        "last_time": last.get("time"),
        "last_close": last.get("close"),
        "change": change,
        "change_pct": change_pct,
        "high": max(c["high"] for c in candles),
        "low": min(c["low"] for c in candles),
        "total_volume": sum((c.get("volume") or 0) for c in candles)
    }
