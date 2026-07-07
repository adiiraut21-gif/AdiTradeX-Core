def get_kite():
    try:
        from auth.kite_session import get_kite_client
        return get_kite_client()
    except Exception:
        try:
            from auth.service import get_kite_client
            return get_kite_client()
        except Exception as e:
            raise RuntimeError(f"Kite client unavailable: {e}")

def classify_position(symbol):
    s = (symbol or "").upper()
    if s.endswith("CE"):
        return "OPTION_CALL"
    if s.endswith("PE"):
        return "OPTION_PUT"
    if "FUT" in s:
        return "FUTURE"
    return "EQUITY"

def normalize_position(p):
    return {
        "tradingsymbol": p.get("tradingsymbol"),
        "exchange": p.get("exchange"),
        "quantity": p.get("quantity", 0),
        "average_price": p.get("average_price", 0),
        "last_price": p.get("last_price", 0),
        "pnl": p.get("pnl", 0),
        "product": p.get("product"),
        "instrument_token": p.get("instrument_token"),
        "position_type": classify_position(p.get("tradingsymbol")),
        "raw": p
    }

def fetch_open_positions():
    kite = get_kite()
    data = kite.positions()
    net_positions = data.get("net", []) if isinstance(data, dict) else []

    active = []
    for p in net_positions:
        if p.get("quantity", 0) != 0:
            active.append(normalize_position(p))

    return {"status": "ok", "count": len(active), "positions": active}
