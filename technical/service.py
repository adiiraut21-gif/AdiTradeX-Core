from datetime import datetime, timedelta
from auth.session_store import get_latest_session
from auth.kite_client import get_kite_client
from technical.symbols import TECHNICAL_SYMBOLS, INTERVAL_MAP
from technical.indicators import ema, rsi, macd, atr, bollinger, vwap
from technical.structure import detect_structure
from technical.scoring import trend_score, momentum_score, volatility_score, structure_score, bias_from_score, grade

def get_kite():
    session = get_latest_session()
    if not session:
        raise RuntimeError("Not logged in. Login with Zerodha first.")
    return get_kite_client(session["access_token"])

def normalize_candles(raw):
    candles = []
    for c in raw:
        candles.append({
            "time": str(c.get("date")),
            "open": c.get("open"),
            "high": c.get("high"),
            "low": c.get("low"),
            "close": c.get("close"),
            "volume": c.get("volume")
        })
    return candles

def fetch_candles(underlying="nifty", interval="15m", days=10):
    key = underlying.lower()
    if key not in TECHNICAL_SYMBOLS:
        raise RuntimeError(f"Unsupported underlying: {underlying}")

    token = TECHNICAL_SYMBOLS[key]["instrument_token"]
    kite = get_kite()

    kite_interval = INTERVAL_MAP.get(interval, "15minute")
    to_date = datetime.now()
    from_date = to_date - timedelta(days=days)

    raw = kite.historical_data(
        instrument_token=token,
        from_date=from_date,
        to_date=to_date,
        interval=kite_interval
    )

    return normalize_candles(raw)

def analyze_technical(underlying="nifty", interval="15m"):
    candles = fetch_candles(underlying, interval)
    if len(candles) < 30:
        raise RuntimeError("Not enough candle data received from Kite.")

    closes = [c["close"] for c in candles]
    latest = candles[-1]
    close = latest["close"]

    ema9 = ema(closes, 9)
    ema20 = ema(closes, 20)
    ema50 = ema(closes, 50)
    ema200 = ema(closes, 200)
    rsi14 = rsi(closes, 14)
    macd_data = macd(closes)
    atr14 = atr(candles, 14)
    bb = bollinger(closes)
    vwap_value = vwap(candles)
    structure = detect_structure(candles)

    t_score = trend_score(close, ema9, ema20, ema50, ema200)
    m_score = momentum_score(rsi14, macd_data)
    v_score = volatility_score(close, atr14)
    s_score = structure_score(structure["structure"])

    technical_score = round((t_score * 0.35) + (m_score * 0.30) + (s_score * 0.20) + (v_score * 0.15), 2)
    bias = bias_from_score(technical_score)

    summary = build_summary(underlying.upper(), close, bias, technical_score, ema9, ema20, rsi14, macd_data, structure)

    return {
        "underlying": underlying.upper(),
        "interval": interval,
        "latest_close": close,
        "latest_time": latest["time"],
        "ema": {
            "ema9": ema9,
            "ema20": ema20,
            "ema50": ema50,
            "ema200": ema200
        },
        "rsi14": rsi14,
        "macd": macd_data,
        "atr14": atr14,
        "bollinger": bb,
        "vwap": vwap_value,
        "structure": structure,
        "scores": {
            "trend_score": t_score,
            "momentum_score": m_score,
            "volatility_score": v_score,
            "structure_score": s_score,
            "technical_score": technical_score,
            "grade": grade(technical_score)
        },
        "technical_bias": bias,
        "summary": summary,
        "candles": candles[-40:]
    }

def build_summary(symbol, close, bias, score, ema9, ema20, rsi14, macd_data, structure):
    parts = [
        f"{symbol} technical bias is {bias} with technical score {score}/100.",
        f"Last close is {close}."
    ]

    if ema9 and ema20:
        if ema9 > ema20:
            parts.append("Short-term EMA alignment is bullish.")
        else:
            parts.append("Short-term EMA alignment is weak or bearish.")

    if rsi14:
        parts.append(f"RSI is {rsi14}, indicating {'bullish momentum' if rsi14 > 55 else 'weak momentum' if rsi14 < 45 else 'neutral momentum'}.")

    hist = macd_data.get("histogram")
    if hist is not None:
        parts.append(f"MACD histogram is {hist}, showing {'positive' if hist > 0 else 'negative'} momentum.")

    parts.append(f"Market structure: {structure['structure']}.")

    return " ".join(parts)
