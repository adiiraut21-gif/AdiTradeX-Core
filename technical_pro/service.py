from datetime import datetime, timedelta
from technical_pro.symbols import TECHNICAL_PRO_SYMBOLS, DEFAULT_TIMEFRAMES, KITE_INTERVALS, LOOKBACK_DAYS
from technical_pro.candles import fetch_raw_candles, candle_summary, get_kite, normalize_candle
from technical_pro.futures_resolver import resolve_current_month_future
from technical_pro.trend_engine import analyze_timeframe_trend, calculate_consensus, build_trend_commentary
from technical_pro.momentum_engine import analyze_timeframe_momentum, calculate_momentum_consensus, build_momentum_commentary
from technical_pro.vwap_engine import analyze_timeframe_vwap, calculate_vwap_consensus
from technical_pro.structure_engine import analyze_timeframe_structure, calculate_structure_consensus
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
            result["timeframes"][tf] = {
                "status": "ok",
                "summary": candle_summary(candles),
                "candles": candles[-80:] if include_candles else []
            }
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

def _fetch_candle_map(key, timeframes):
    candle_map = {}
    summaries = {}

    for tf in timeframes:
        try:
            candles = fetch_raw_candles(key, tf)
            candle_map[tf] = candles
            summaries[tf] = candle_summary(candles)
        except Exception as e:
            candle_map[tf] = None
            summaries[tf] = {"status": "error", "error": str(e)}

    return candle_map, summaries

def _fetch_futures_candle_map(key, timeframes):
    kite = get_kite()
    future = resolve_current_month_future(kite, key)

    candle_map = {}
    summaries = {}

    for tf in timeframes:
        try:
            if tf == "75m":
                base = _fetch_future_raw_candles(kite, future["instrument_token"], "15m")
                candles = _resample_to_75m(base)
            else:
                candles = _fetch_future_raw_candles(kite, future["instrument_token"], tf)

            candle_map[tf] = candles
            summaries[tf] = candle_summary(candles)
        except Exception as e:
            candle_map[tf] = None
            summaries[tf] = {"status": "error", "error": str(e)}

    return candle_map, summaries, future

def _fetch_future_raw_candles(kite, instrument_token, timeframe):
    kite_interval = KITE_INTERVALS.get(timeframe)
    if not kite_interval:
        raise RuntimeError(f"Unsupported futures timeframe: {timeframe}")

    days = LOOKBACK_DAYS.get(timeframe, 10)
    to_date = datetime.now()
    from_date = to_date - timedelta(days=days)

    raw = kite.historical_data(
        instrument_token=instrument_token,
        from_date=from_date,
        to_date=to_date,
        interval=kite_interval
    )

    return [normalize_candle(c) for c in raw]

def _resample_to_75m(candles):
    if not candles:
        return []

    grouped = []
    bucket = []

    for candle in candles:
        bucket.append(candle)
        if len(bucket) == 5:
            grouped.append({
                "time": bucket[0]["time"],
                "open": bucket[0]["open"],
                "high": max(c["high"] for c in bucket),
                "low": min(c["low"] for c in bucket),
                "close": bucket[-1]["close"],
                "volume": sum((c.get("volume") or 0) for c in bucket)
            })
            bucket = []

    if bucket:
        grouped.append({
            "time": bucket[0]["time"],
            "open": bucket[0]["open"],
            "high": max(c["high"] for c in bucket),
            "low": min(c["low"] for c in bucket),
            "close": bucket[-1]["close"],
            "volume": sum((c.get("volume") or 0) for c in bucket)
        })

    return grouped

def _run_engine_from_candle_map(candle_map, analyzer):
    results = {}
    for tf, candles in candle_map.items():
        if candles is None:
            results[tf] = {"timeframe": tf, "status": "error", "error": "Could not fetch candles"}
        else:
            try:
                results[tf] = analyzer(tf, candles)
            except Exception as e:
                results[tf] = {"timeframe": tf, "status": "error", "error": str(e)}
    return results

def get_trend_intelligence(underlying="nifty", timeframes=None):
    key = underlying.lower()
    if key not in TECHNICAL_PRO_SYMBOLS:
        raise RuntimeError(f"Unsupported underlying: {underlying}")
    if timeframes is None:
        timeframes = DEFAULT_TIMEFRAMES

    candle_map, summaries = _fetch_candle_map(key, timeframes)
    results = _run_engine_from_candle_map(candle_map, analyze_timeframe_trend)
    consensus = calculate_consensus(results)

    return {
        "underlying": TECHNICAL_PRO_SYMBOLS[key]["display"],
        "symbol_key": key,
        "consensus": consensus,
        "timeframes": results,
        "candle_summaries": summaries,
        "commentary": build_trend_commentary(TECHNICAL_PRO_SYMBOLS[key]["display"], consensus, results)
    }

def get_momentum_intelligence(underlying="nifty", timeframes=None):
    key = underlying.lower()
    if key not in TECHNICAL_PRO_SYMBOLS:
        raise RuntimeError(f"Unsupported underlying: {underlying}")
    if timeframes is None:
        timeframes = DEFAULT_TIMEFRAMES

    candle_map, summaries = _fetch_candle_map(key, timeframes)
    results = _run_engine_from_candle_map(candle_map, analyze_timeframe_momentum)
    consensus = calculate_momentum_consensus(results)

    return {
        "underlying": TECHNICAL_PRO_SYMBOLS[key]["display"],
        "symbol_key": key,
        "consensus": consensus,
        "timeframes": results,
        "candle_summaries": summaries,
        "commentary": build_momentum_commentary(TECHNICAL_PRO_SYMBOLS[key]["display"], consensus, results)
    }

def get_vwap_intelligence(underlying="nifty", timeframes=None):
    key = underlying.lower()
    if key not in TECHNICAL_PRO_SYMBOLS:
        raise RuntimeError(f"Unsupported underlying: {underlying}")
    if timeframes is None:
        timeframes = DEFAULT_TIMEFRAMES

    futures_map, summaries, future = _fetch_futures_candle_map(key, timeframes)

    results = {}
    for tf, candles in futures_map.items():
        if candles is None:
            results[tf] = {"timeframe": tf, "status": "error", "error": "Could not fetch futures candles"}
        else:
            try:
                results[tf] = analyze_timeframe_vwap(tf, candles, source=future["tradingsymbol"])
            except Exception as e:
                results[tf] = {"timeframe": tf, "status": "error", "error": str(e), "vwap_source": future["tradingsymbol"]}

    consensus = calculate_vwap_consensus(results)

    return {
        "underlying": TECHNICAL_PRO_SYMBOLS[key]["display"],
        "symbol_key": key,
        "vwap_source": "current_month_futures",
        "future_contract": future,
        "consensus": consensus,
        "timeframes": results,
        "candle_summaries": summaries,
        "commentary": f"{TECHNICAL_PRO_SYMBOLS[key]['display']} VWAP is calculated from {future['tradingsymbol']} futures volume. VWAP bias is {consensus.get('overall_vwap')} with average VWAP score {consensus.get('average_vwap_score')}/100."
    }

def get_structure_intelligence(underlying="nifty", timeframes=None):
    key = underlying.lower()
    if key not in TECHNICAL_PRO_SYMBOLS:
        raise RuntimeError(f"Unsupported underlying: {underlying}")
    if timeframes is None:
        timeframes = DEFAULT_TIMEFRAMES

    candle_map, summaries = _fetch_candle_map(key, timeframes)
    results = _run_engine_from_candle_map(candle_map, analyze_timeframe_structure)
    consensus = calculate_structure_consensus(results)

    return {
        "underlying": TECHNICAL_PRO_SYMBOLS[key]["display"],
        "symbol_key": key,
        "consensus": consensus,
        "timeframes": results,
        "candle_summaries": summaries,
        "commentary": f"{TECHNICAL_PRO_SYMBOLS[key]['display']} structure intelligence shows {consensus.get('overall_structure')} structure with average structure score {consensus.get('average_structure_score')}/100."
    }

def get_technical_intelligence_snapshot(underlying="nifty", timeframes=None):
    key = underlying.lower()
    if key not in TECHNICAL_PRO_SYMBOLS:
        raise RuntimeError(f"Unsupported underlying: {underlying}")
    if timeframes is None:
        timeframes = DEFAULT_TIMEFRAMES

    candle_map, summaries = _fetch_candle_map(key, timeframes)

    trend_results = _run_engine_from_candle_map(candle_map, analyze_timeframe_trend)
    momentum_results = _run_engine_from_candle_map(candle_map, analyze_timeframe_momentum)
    structure_results = _run_engine_from_candle_map(candle_map, analyze_timeframe_structure)

    trend_consensus = calculate_consensus(trend_results)
    momentum_consensus = calculate_momentum_consensus(momentum_results)
    structure_consensus = calculate_structure_consensus(structure_results)

    try:
        futures_map, futures_summaries, future = _fetch_futures_candle_map(key, timeframes)
        vwap_results = {}
        for tf, candles in futures_map.items():
            if candles is None:
                vwap_results[tf] = {"timeframe": tf, "status": "error", "error": "Could not fetch futures candles"}
            else:
                vwap_results[tf] = analyze_timeframe_vwap(tf, candles, source=future["tradingsymbol"])
        vwap_consensus = calculate_vwap_consensus(vwap_results)
        vwap_commentary = f"{TECHNICAL_PRO_SYMBOLS[key]['display']} VWAP uses {future['tradingsymbol']} futures volume and shows {vwap_consensus.get('overall_vwap')} VWAP bias."
    except Exception as e:
        future = None
        vwap_consensus = {"overall_vwap": "Unknown", "vwap_consensus": 0, "average_vwap_score": 0, "aligned_timeframes": 0, "total_timeframes": 0}
        vwap_commentary = f"Futures VWAP unavailable: {str(e)}"

    trend_score = trend_consensus.get("average_trend_score", 50)
    momentum_score = momentum_consensus.get("average_momentum_score", 50)
    vwap_score = vwap_consensus.get("average_vwap_score", 50)
    structure_score = structure_consensus.get("average_structure_score", 50)

    technical_score = round((trend_score * 0.35) + (momentum_score * 0.25) + (structure_score * 0.25) + (vwap_score * 0.15), 2)

    if technical_score >= 75:
        bias = "Bullish"
    elif technical_score <= 35:
        bias = "Bearish"
    else:
        bias = "Neutral"

    return {
        "underlying": TECHNICAL_PRO_SYMBOLS[key]["display"],
        "technical_score": technical_score,
        "technical_bias": bias,
        "vwap_source": "current_month_futures",
        "future_contract": future,
        "trend": trend_consensus,
        "momentum": momentum_consensus,
        "structure": structure_consensus,
        "vwap": vwap_consensus,
        "trend_commentary": build_trend_commentary(TECHNICAL_PRO_SYMBOLS[key]["display"], trend_consensus, trend_results),
        "momentum_commentary": build_momentum_commentary(TECHNICAL_PRO_SYMBOLS[key]["display"], momentum_consensus, momentum_results),
        "vwap_commentary": vwap_commentary,
        "structure_commentary": f"{TECHNICAL_PRO_SYMBOLS[key]['display']} structure intelligence shows {structure_consensus.get('overall_structure')} structure."
    }
