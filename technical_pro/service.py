from technical_pro.symbols import TECHNICAL_PRO_SYMBOLS, DEFAULT_TIMEFRAMES
from technical_pro.candles import fetch_raw_candles, candle_summary
from technical_pro.trend_engine import analyze_timeframe_trend, calculate_consensus, build_trend_commentary
from technical_pro.momentum_engine import analyze_timeframe_momentum, calculate_momentum_consensus, build_momentum_commentary
from database.db import log_event

def get_multi_timeframe_data(underlying="nifty", timeframes=None, include_candles=False):
    key = underlying.lower()
    if key not in TECHNICAL_PRO_SYMBOLS:
        raise RuntimeError(f"Unsupported underlying: {underlying}")

    if timeframes is None:
        timeframes = DEFAULT_TIMEFRAMES

    result = {"underlying": TECHNICAL_PRO_SYMBOLS[key]["display"], "symbol_key": key, "timeframes": {}}

    for tf in timeframes:
        try:
            candles = fetch_raw_candles(key, tf)
            summary = candle_summary(candles)
            result["timeframes"][tf] = {"status": "ok", "summary": summary, "candles": candles[-80:] if include_candles else []}
        except Exception as e:
            result["timeframes"][tf] = {"status": "error", "error": str(e), "summary": None, "candles": []}

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

def get_trend_intelligence(underlying="nifty", timeframes=None):
    key = underlying.lower()
    if key not in TECHNICAL_PRO_SYMBOLS:
        raise RuntimeError(f"Unsupported underlying: {underlying}")

    if timeframes is None:
        timeframes = DEFAULT_TIMEFRAMES

    results = {}
    candle_summaries = {}

    for tf in timeframes:
        try:
            candles = fetch_raw_candles(key, tf)
            candle_summaries[tf] = candle_summary(candles)
            results[tf] = analyze_timeframe_trend(tf, candles)
        except Exception as e:
            results[tf] = {"timeframe": tf, "status": "error", "error": str(e)}

    consensus = calculate_consensus(results)
    commentary = build_trend_commentary(TECHNICAL_PRO_SYMBOLS[key]["display"], consensus, results)

    log_event("TREND_ENGINE", f"Trend intelligence generated for {key}")

    return {
        "underlying": TECHNICAL_PRO_SYMBOLS[key]["display"],
        "symbol_key": key,
        "consensus": consensus,
        "timeframes": results,
        "candle_summaries": candle_summaries,
        "commentary": commentary
    }

def get_momentum_intelligence(underlying="nifty", timeframes=None):
    key = underlying.lower()
    if key not in TECHNICAL_PRO_SYMBOLS:
        raise RuntimeError(f"Unsupported underlying: {underlying}")

    if timeframes is None:
        timeframes = DEFAULT_TIMEFRAMES

    results = {}
    candle_summaries = {}

    for tf in timeframes:
        try:
            candles = fetch_raw_candles(key, tf)
            candle_summaries[tf] = candle_summary(candles)
            results[tf] = analyze_timeframe_momentum(tf, candles)
        except Exception as e:
            results[tf] = {"timeframe": tf, "status": "error", "error": str(e)}

    consensus = calculate_momentum_consensus(results)
    commentary = build_momentum_commentary(TECHNICAL_PRO_SYMBOLS[key]["display"], consensus, results)

    log_event("MOMENTUM_ENGINE", f"Momentum intelligence generated for {key}")

    return {
        "underlying": TECHNICAL_PRO_SYMBOLS[key]["display"],
        "symbol_key": key,
        "consensus": consensus,
        "timeframes": results,
        "candle_summaries": candle_summaries,
        "commentary": commentary
    }

def get_technical_intelligence_snapshot(underlying="nifty"):
    trend = get_trend_intelligence(underlying)
    momentum = get_momentum_intelligence(underlying)

    trend_score = trend["consensus"].get("average_trend_score", 50)
    momentum_score = momentum["consensus"].get("average_momentum_score", 50)

    technical_score = round((trend_score * 0.55) + (momentum_score * 0.45), 2)

    if technical_score >= 75:
        bias = "Bullish"
    elif technical_score <= 35:
        bias = "Bearish"
    else:
        bias = "Neutral"

    return {
        "underlying": trend["underlying"],
        "technical_score": technical_score,
        "technical_bias": bias,
        "trend": trend["consensus"],
        "momentum": momentum["consensus"],
        "trend_commentary": trend["commentary"],
        "momentum_commentary": momentum["commentary"]
    }
