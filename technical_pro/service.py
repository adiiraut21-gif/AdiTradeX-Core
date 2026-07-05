from technical_pro.symbols import TECHNICAL_PRO_SYMBOLS, DEFAULT_TIMEFRAMES
from technical_pro.candles import fetch_raw_candles, candle_summary
from database.db import log_event

def get_multi_timeframe_data(underlying="nifty", timeframes=None, include_candles=False):
    key = underlying.lower()
    if key not in TECHNICAL_PRO_SYMBOLS:
        raise RuntimeError(f"Unsupported underlying: {underlying}")

    if timeframes is None:
        timeframes = DEFAULT_TIMEFRAMES

    result = {
        "underlying": TECHNICAL_PRO_SYMBOLS[key]["display"],
        "symbol_key": key,
        "timeframes": {}
    }

    for tf in timeframes:
        try:
            candles = fetch_raw_candles(key, tf)
            summary = candle_summary(candles)
            result["timeframes"][tf] = {
                "status": "ok",
                "summary": summary,
                "candles": candles[-80:] if include_candles else []
            }
        except Exception as e:
            result["timeframes"][tf] = {
                "status": "error",
                "error": str(e),
                "summary": None,
                "candles": []
            }

    log_event("TECHNICAL_PRO", f"Multi-timeframe data fetched for {key}")
    return result

def get_timeframe_snapshot(underlying="nifty", timeframe="15m"):
    candles = fetch_raw_candles(underlying.lower(), timeframe)
    return {
        "underlying": TECHNICAL_PRO_SYMBOLS[underlying.lower()]["display"],
        "timeframe": timeframe,
        "summary": candle_summary(candles),
        "candles": candles[-120:]
    }
