def get_kite():
    try:
        from auth.kite_session import get_kite_client
        return get_kite_client()
    except Exception:
        try:
            from auth.service import get_kite_client
            return get_kite_client()
        except Exception:
            try:
                from kiteconnect import KiteConnect
                from config.settings import Settings
                kite = KiteConnect(api_key=Settings.KITE_API_KEY)
                return kite
            except Exception as e:
                raise RuntimeError(f"Kite client unavailable: {e}")

def fetch_open_positions():
    kite = get_kite()
    data = kite.positions()
    net_positions = data.get("net", []) if isinstance(data, dict) else []

    active = []
    for p in net_positions:
        qty = p.get("quantity", 0)
        if qty != 0:
            active.append(normalize_position(p))

    return {
        "status": "ok",
        "count": len(active),
        "positions": active
    }

def normalize_position(p):
    tradingsymbol = p.get("tradingsymbol")
    quantity = p.get("quantity", 0)
    avg = p.get("average_price", 0)
    last = p.get("last_price", 0)

    return {
        "tradingsymbol": tradingsymbol,
        "exchange": p.get("exchange"),
        "quantity": quantity,
        "average_price": avg,
        "last_price": last,
        "pnl": p.get("pnl", 0),
        "product": p.get("product"),
        "instrument_token": p.get("instrument_token"),
        "position_type": classify_position(tradingsymbol),
        "raw": p
    }

def classify_position(symbol):
    s = (symbol or "").upper()
    if s.endswith("CE"):
        return "OPTION_CALL"
    if s.endswith("PE"):
        return "OPTION_PUT"
    if "FUT" in s:
        return "FUTURE"
    return "EQUITY"
