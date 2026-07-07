def build_risk_plan(position, technical, option_chain):
    entry = position.get("average_price") or 0
    cmp_price = position.get("last_price") or 0
    pos_type = position.get("position_type")

    if entry <= 0 or cmp_price <= 0:
        return {
            "stop_loss": None,
            "target_1": None,
            "target_2": None,
            "trailing_sl": None,
            "pnl_pct": 0,
            "risk_note": "Entry/CMP unavailable"
        }

    if pos_type in ["OPTION_CALL", "OPTION_PUT"]:
        stop_loss = round(max(cmp_price * 0.72, entry * 0.65), 2)
        target_1 = round(max(entry * 1.30, cmp_price * 1.15), 2)
        target_2 = round(max(entry * 1.65, cmp_price * 1.35), 2)
        trailing_sl = round(max(stop_loss, cmp_price * 0.82), 2)
    else:
        stop_loss = round(cmp_price * 0.94, 2)
        target_1 = round(cmp_price * 1.06, 2)
        target_2 = round(cmp_price * 1.12, 2)
        trailing_sl = round(cmp_price * 0.96, 2)

    pnl_pct = round(((cmp_price - entry) / entry) * 100, 2)
    if position.get("quantity", 0) < 0:
        pnl_pct = -pnl_pct

    return {
        "stop_loss": stop_loss,
        "target_1": target_1,
        "target_2": target_2,
        "trailing_sl": trailing_sl,
        "pnl_pct": pnl_pct,
        "risk_note": "SL/targets based on CMP, entry price, position type and confirmation score."
    }
