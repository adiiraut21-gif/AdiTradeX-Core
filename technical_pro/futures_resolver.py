from datetime import datetime

FUTURE_NAME_MAP = {
    "nifty": "NIFTY",
    "banknifty": "BANKNIFTY",
    "finnifty": "FINNIFTY",
    "midcpnifty": "MIDCPNIFTY"
}

def resolve_current_month_future(kite, underlying="nifty"):
    key = underlying.lower()
    fut_name = FUTURE_NAME_MAP.get(key)
    if not fut_name:
        raise RuntimeError(f"Unsupported futures underlying: {underlying}")

    instruments = kite.instruments("NFO")
    today = datetime.now().date()

    candidates = []
    for inst in instruments:
        if inst.get("segment") != "NFO-FUT":
            continue

        name = inst.get("name")
        tradingsymbol = inst.get("tradingsymbol", "")
        expiry = inst.get("expiry")

        if name != fut_name and not tradingsymbol.startswith(fut_name):
            continue

        if expiry and expiry >= today:
            candidates.append(inst)

    if not candidates:
        raise RuntimeError(f"No active futures contract found for {fut_name}")

    candidates = sorted(candidates, key=lambda x: x.get("expiry"))
    selected = candidates[0]

    return {
        "instrument_token": selected["instrument_token"],
        "tradingsymbol": selected["tradingsymbol"],
        "name": selected.get("name"),
        "expiry": str(selected.get("expiry")),
        "exchange": selected.get("exchange", "NFO")
    }
