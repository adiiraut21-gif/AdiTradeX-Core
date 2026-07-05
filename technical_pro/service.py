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
            result["timeframes"][tf] = {"status": "ok", "summary": candle_summary(candles), "candles": candles[-80:] if include_candles else []}
        except Exception as e:
            result["timeframes"][tf] = {"status": "error", "error": str(e), "summary": None, "candles": []}
    log_event("TECHNICAL_PRO", f"Multi-timeframe data fetched for {key}")
    return result

def get_timeframe_snapshot(underlying="nifty", timeframe="15m"):
    candles = fetch_raw_candles(underlying.lower(), timeframe)
    return {"underlying": TECHNICAL_PRO_SYMBOLS[underlying.lower()]["display"], "timeframe": timeframe, "summary": candle_summary(candles), "candles": candles[-120:]}

def _run_engine(underlying, analyzer, consensus_fn, engine_name, timeframes=None):
    key = underlying.lower()
    if key not in TECHNICAL_PRO_SYMBOLS:
        raise RuntimeError(f"Unsupported underlying: {underlying}")
    if timeframes is None:
        timeframes = DEFAULT_TIMEFRAMES
    results = {}
    summaries = {}
    for tf in timeframes:
        try:
            candles = fetch_raw_candles(key, tf)
            summaries[tf] = candle_summary(candles)
            results[tf] = analyzer(tf, candles)
        except Exception as e:
            results[tf] = {"timeframe": tf, "status": "error", "error": str(e)}
    consensus = consensus_fn(results)
    log_event(engine_name, f"{engine_name} generated for {key}")
    return {"underlying": TECHNICAL_PRO_SYMBOLS[key]["display"], "symbol_key": key, "consensus": consensus, "timeframes": results, "candle_summaries": summaries}

def get_trend_intelligence(underlying="nifty", timeframes=None):
    data = _run_engine(underlying, analyze_timeframe_trend, calculate_consensus, "TREND_ENGINE", timeframes)
    data["commentary"] = build_trend_commentary(data["underlying"], data["consensus"], data["timeframes"])
    return data

def get_momentum_intelligence(underlying="nifty", timeframes=None):
    data = _run_engine(underlying, analyze_timeframe_momentum, calculate_momentum_consensus, "MOMENTUM_ENGINE", timeframes)
    data["commentary"] = build_momentum_commentary(data["underlying"], data["consensus"], data["timeframes"])
    return data

def get_vwap_intelligence(underlying="nifty", timeframes=None):
    data = _run_engine(underlying, analyze_timeframe_vwap, calculate_vwap_consensus, "VWAP_ENGINE", timeframes)
    data["commentary"] = f"{data['underlying']} VWAP intelligence shows {data['consensus']['overall_vwap']} VWAP bias with average VWAP score {data['consensus']['average_vwap_score']}/100."
    return data

def get_structure_intelligence(underlying="nifty", timeframes=None):
    data = _run_engine(underlying, analyze_timeframe_structure, calculate_structure_consensus, "STRUCTURE_ENGINE", timeframes)
    data["commentary"] = f"{data['underlying']} structure intelligence shows {data['consensus']['overall_structure']} structure with average structure score {data['consensus']['average_structure_score']}/100."
    return data

def get_technical_intelligence_snapshot(underlying="nifty"):
    trend = get_trend_intelligence(underlying)
    momentum = get_momentum_intelligence(underlying)
    vwap = get_vwap_intelligence(underlying)
    structure = get_structure_intelligence(underlying)

    trend_score = trend["consensus"].get("average_trend_score", 50)
    momentum_score = momentum["consensus"].get("average_momentum_score", 50)
    vwap_score = vwap["consensus"].get("average_vwap_score", 50)
    structure_score = structure["consensus"].get("average_structure_score", 50)

    technical_score = round((trend_score * 0.35) + (momentum_score * 0.25) + (structure_score * 0.25) + (vwap_score * 0.15), 2)

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
        "structure": structure["consensus"],
        "vwap": vwap["consensus"],
        "trend_commentary": trend["commentary"],
        "momentum_commentary": momentum["commentary"],
        "structure_commentary": structure["commentary"],
        "vwap_commentary": vwap["commentary"]
    }
