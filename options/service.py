from collections import defaultdict
from datetime import date
from auth.kite_client import get_kite_client
from auth.session_store import get_latest_session
from market.service import fetch_quotes
from database.db import log_event

_INSTRUMENT_CACHE = None

UNDERLYING_MAP = {
    "nifty": {
        "spot": "NSE:NIFTY 50",
        "name": "NIFTY",
        "step": 50
    },
    "banknifty": {
        "spot": "NSE:NIFTY BANK",
        "name": "BANKNIFTY",
        "step": 100
    },
    "finnifty": {
        "spot": "NSE:NIFTY FIN SERVICE",
        "name": "FINNIFTY",
        "step": 50
    },
    "midcpnifty": {
        "spot": "NSE:NIFTY MID SELECT",
        "name": "MIDCPNIFTY",
        "step": 25
    }
}

def require_session():
    session = get_latest_session()
    if not session:
        raise RuntimeError("Not logged in. Login with Zerodha first.")
    return session

def kite():
    session = require_session()
    return get_kite_client(session["access_token"])

def get_nfo_instruments(force_refresh=False):
    global _INSTRUMENT_CACHE
    if _INSTRUMENT_CACHE is None or force_refresh:
        k = kite()
        _INSTRUMENT_CACHE = k.instruments("NFO")
        log_event("OPTIONS", f"NFO instruments loaded: {len(_INSTRUMENT_CACHE)}")
    return _INSTRUMENT_CACHE

def get_spot_price(underlying_key):
    cfg = UNDERLYING_MAP[underlying_key]
    data = fetch_quotes([cfg["spot"]])
    return data[cfg["spot"]]["last_price"]

def nearest_expiry(instruments, name):
    expiries = sorted({
        i["expiry"] for i in instruments
        if i.get("name") == name and i.get("segment") == "NFO-OPT"
    })
    today = date.today()
    expiries = [e for e in expiries if e >= today]
    return expiries[0] if expiries else None

def build_option_chain(underlying_key="nifty", strikes_each_side=8):
    underlying_key = underlying_key.lower()
    if underlying_key not in UNDERLYING_MAP:
        raise RuntimeError(f"Unsupported underlying: {underlying_key}")

    cfg = UNDERLYING_MAP[underlying_key]
    name = cfg["name"]
    step = cfg["step"]

    spot = get_spot_price(underlying_key)
    atm = round(spot / step) * step

    instruments = get_nfo_instruments()
    expiry = nearest_expiry(instruments, name)
    if not expiry:
        raise RuntimeError(f"No expiry found for {name}")

    min_strike = atm - strikes_each_side * step
    max_strike = atm + strikes_each_side * step

    selected = [
        i for i in instruments
        if i.get("name") == name
        and i.get("segment") == "NFO-OPT"
        and i.get("expiry") == expiry
        and min_strike <= i.get("strike", 0) <= max_strike
    ]

    quote_symbols = [f"NFO:{i['tradingsymbol']}" for i in selected]
    quote_data = kite().quote(quote_symbols) if quote_symbols else {}

    rows = defaultdict(lambda: {"CE": None, "PE": None})

    total_call_oi = 0
    total_put_oi = 0

    for inst in selected:
        symbol = f"NFO:{inst['tradingsymbol']}"
        q = quote_data.get(symbol, {})
        ohlc = q.get("ohlc", {}) or {}

        item = {
            "tradingsymbol": inst["tradingsymbol"],
            "strike": inst["strike"],
            "type": inst["instrument_type"],
            "ltp": q.get("last_price"),
            "oi": q.get("oi") or 0,
            "volume": q.get("volume"),
            "open": ohlc.get("open"),
            "high": ohlc.get("high"),
            "low": ohlc.get("low"),
            "close": ohlc.get("close"),
        }

        if inst["instrument_type"] == "CE":
            rows[inst["strike"]]["CE"] = item
            total_call_oi += item["oi"]
        elif inst["instrument_type"] == "PE":
            rows[inst["strike"]]["PE"] = item
            total_put_oi += item["oi"]

    chain = []
    for strike in sorted(rows.keys()):
        ce = rows[strike]["CE"] or {}
        pe = rows[strike]["PE"] or {}

        call_oi = ce.get("oi", 0)
        put_oi = pe.get("oi", 0)

        chain.append({
            "strike": strike,
            "is_atm": strike == atm,
            "ce_ltp": ce.get("ltp"),
            "ce_oi": call_oi,
            "ce_volume": ce.get("volume"),
            "pe_ltp": pe.get("ltp"),
            "pe_oi": put_oi,
            "pe_volume": pe.get("volume"),
        })

    pcr = round(total_put_oi / total_call_oi, 2) if total_call_oi else None
    max_pain = approximate_max_pain(chain)

    return {
        "underlying": underlying_key.upper(),
        "spot_symbol": cfg["spot"],
        "spot": spot,
        "atm": atm,
        "expiry": str(expiry),
        "pcr": pcr,
        "total_call_oi": total_call_oi,
        "total_put_oi": total_put_oi,
        "max_pain": max_pain,
        "chain": chain
    }

def approximate_max_pain(chain):
    if not chain:
        return None

    strikes = [r["strike"] for r in chain]
    pain_by_strike = {}

    for expiry_price in strikes:
        pain = 0
        for r in chain:
            strike = r["strike"]
            call_oi = r.get("ce_oi") or 0
            put_oi = r.get("pe_oi") or 0

            if expiry_price > strike:
                pain += (expiry_price - strike) * call_oi
            if expiry_price < strike:
                pain += (strike - expiry_price) * put_oi

        pain_by_strike[expiry_price] = pain

    return min(pain_by_strike, key=pain_by_strike.get)
