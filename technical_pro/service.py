from technical_pro.symbols import TECHNICAL_PRO_SYMBOLS, DEFAULT_TIMEFRAMES
from technical_pro.candles import fetch_raw_candles, candle_summary
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

    candle_map, summaries = _fetch_candle_map(key, timeframes)
    results = _run_engine_from_candle_map(candle_map, analyze_timeframe_vwap)
    consensus = calculate_vwap_consensus(results)

    return {
        "underlying": TECHNICAL_PRO_SYMBOLS[key]["display"],
        "symbol_key": key,
        "consensus": consensus,
        "timeframes": results,
        "candle_summaries": summaries,
        "commentary": f"{TECHNICAL_PRO_SYMBOLS[key]['display']} VWAP intelligence shows {consensus.get('overall_vwap')} VWAP bias with average VWAP score {consensus.get('average_vwap_score')}/100."
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

    # Fetch candles only once, then run all engines on same data.
    candle_map, summaries = _fetch_candle_map(key, timeframes)

    trend_results = _run_engine_from_candle_map(candle_map, analyze_timeframe_trend)
    momentum_results = _run_engine_from_candle_map(candle_map, analyze_timeframe_momentum)
    vwap_results = _run_engine_from_candle_map(candle_map, analyze_timeframe_vwap)
    structure_results = _run_engine_from_candle_map(candle_map, analyze_timeframe_structure)

    trend_consensus = calculate_consensus(trend_results)
    momentum_consensus = calculate_momentum_consensus(momentum_results)
    vwap_consensus = calculate_vwap_consensus(vwap_results)
    structure_consensus = calculate_structure_consensus(structure_results)

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
        "trend": trend_consensus,
        "momentum": momentum_consensus,
        "structure": structure_consensus,
        "vwap": vwap_consensus,
        "trend_commentary": build_trend_commentary(TECHNICAL_PRO_SYMBOLS[key]["display"], trend_consensus, trend_results),
        "momentum_commentary": build_momentum_commentary(TECHNICAL_PRO_SYMBOLS[key]["display"], momentum_consensus, momentum_results),
        "vwap_commentary": f"{TECHNICAL_PRO_SYMBOLS[key]['display']} VWAP intelligence shows {vwap_consensus.get('overall_vwap')} VWAP bias.",
        "structure_commentary": f"{TECHNICAL_PRO_SYMBOLS[key]['display']} structure intelligence shows {structure_consensus.get('overall_structure')} structure."
    }
