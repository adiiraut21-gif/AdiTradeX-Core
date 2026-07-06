from strategy.dynamic_spread_optimizer import optimize_debit_spread, optimize_credit_spread

def _num(x, default=0):
    try:
        if x is None:
            return default
        return float(x)
    except Exception:
        return default


def _get(row, *keys, default=None):
    for k in keys:
        if k in row and row.get(k) is not None:
            return row.get(k)
    return default


def _normalise_chain_row(row):
    return {
        "strike": _num(_get(row, "strike", "strike_price", "strikePrice")),
        "ce_ltp": _num(_get(row, "ce_ltp", "CE_LTP", "call_ltp", "callLTP")),
        "pe_ltp": _num(_get(row, "pe_ltp", "PE_LTP", "put_ltp", "putLTP")),
        "ce_oi": _num(_get(row, "ce_oi", "CE_OI", "call_oi", "callOI")),
        "pe_oi": _num(_get(row, "pe_oi", "PE_OI", "put_oi", "putOI")),
        "ce_volume": _num(_get(row, "ce_volume", "CE_VOLUME", "call_volume", "callVolume")),
        "pe_volume": _num(_get(row, "pe_volume", "PE_VOLUME", "put_volume", "putVolume")),
        "raw": row
    }


def _chain_map(chain):
    rows = [_normalise_chain_row(r) for r in chain if r]
    rows = [r for r in rows if r["strike"] > 0]
    rows = sorted(rows, key=lambda x: x["strike"])
    return rows, {r["strike"]: r for r in rows}


def _nearest_strike(rows, target):
    if not rows:
        return None
    return min(rows, key=lambda x: abs(x["strike"] - target))["strike"]


def _step(rows, default=50):
    strikes = sorted({r["strike"] for r in rows})
    diffs = [strikes[i + 1] - strikes[i] for i in range(len(strikes) - 1) if strikes[i + 1] - strikes[i] > 0]
    return int(min(diffs)) if diffs else default


def _leg(row, action, opt_type):
    if not row:
        return None

    if opt_type == "CE":
        premium, oi, volume = row["ce_ltp"], row["ce_oi"], row["ce_volume"]
    else:
        premium, oi, volume = row["pe_ltp"], row["pe_oi"], row["pe_volume"]

    return {
        "action": action,
        "strike": int(row["strike"]),
        "type": opt_type,
        "premium": round(premium, 2),
        "oi": int(oi),
        "volume": int(volume),
        "display": f"{action} {int(row['strike'])} {opt_type} @ {round(premium, 2)}"
    }


def _expiry(analytics):
    return analytics.get("expiry") or analytics.get("nearest_expiry") or analytics.get("selected_expiry") or "Current Weekly"


def _calc_long(leg):
    premium = leg["premium"]
    breakeven = round(leg["strike"] + premium, 2) if leg["type"] == "CE" else round(leg["strike"] - premium, 2)
    return {
        "net_debit": premium,
        "net_credit": 0,
        "max_profit": "Open",
        "max_loss": premium,
        "breakeven": breakeven,
        "risk_reward": "Open",
        "score": 50,
        "reason": "Single-leg directional trade."
    }


def build_live_option_legs(strategy_name, analytics):
    chain = analytics.get("chain") or []
    rows, by_strike = _chain_map(chain)

    if not rows:
        return {"status": "error", "reason": "Live option chain is not available.", "strategy": strategy_name, "legs": []}

    spot = _num(analytics.get("spot") or analytics.get("underlying_value"))
    atm = analytics.get("atm") or _nearest_strike(rows, spot)
    atm = _nearest_strike(rows, _num(atm))
    step = _step(rows)

    if not atm:
        return {"status": "error", "reason": "ATM strike could not be resolved from option chain.", "strategy": strategy_name, "legs": []}

    expiry = _expiry(analytics)
    name = (strategy_name or "").lower()
    legs = []
    calc = {}
    optimizer = None

    if "long call" in name:
        buy = _leg(by_strike.get(atm), "BUY", "CE")
        legs = [buy]
        calc = _calc_long(buy)

    elif "long put" in name:
        buy = _leg(by_strike.get(atm), "BUY", "PE")
        legs = [buy]
        calc = _calc_long(buy)

    elif "bull call" in name:
        optimizer = optimize_debit_spread(rows, by_strike, atm, step, spot, "CE", "bull")
        if optimizer:
            legs, calc = optimizer["legs"], optimizer["calculation"]

    elif "bear put" in name:
        optimizer = optimize_debit_spread(rows, by_strike, atm, step, spot, "PE", "bear")
        if optimizer:
            legs, calc = optimizer["legs"], optimizer["calculation"]

    elif "bull put" in name:
        optimizer = optimize_credit_spread(rows, by_strike, atm, step, spot, "PE", "bull")
        if optimizer:
            legs, calc = optimizer["legs"], optimizer["calculation"]

    elif "bear call" in name:
        optimizer = optimize_credit_spread(rows, by_strike, atm, step, spot, "CE", "bear")
        if optimizer:
            legs, calc = optimizer["legs"], optimizer["calculation"]

    else:
        return {"status": "no_trade", "reason": "No option legs required for No Trade or unsupported strategy.", "strategy": strategy_name, "expiry": expiry, "legs": []}

    if not legs or any(l is None for l in legs):
        return {"status": "error", "reason": "One or more option legs could not be built from live chain.", "strategy": strategy_name, "expiry": expiry, "legs": []}

    return {
        "status": "ok",
        "strategy": strategy_name,
        "expiry": expiry,
        "atm": int(atm),
        "step": step,
        "legs": legs,
        "calculation": calc,
        "optimizer": {
            "enabled": optimizer is not None,
            "candidate_count": optimizer.get("candidate_count") if optimizer else 1,
            "all_candidates": optimizer.get("all_candidates") if optimizer else []
        }
    }
