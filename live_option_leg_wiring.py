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
    strike = _num(_get(row, "strike", "strike_price", "strikePrice"))

    ce_ltp = _num(_get(row, "ce_ltp", "CE_LTP", "call_ltp", "callLTP"))
    pe_ltp = _num(_get(row, "pe_ltp", "PE_LTP", "put_ltp", "putLTP"))

    ce_oi = _num(_get(row, "ce_oi", "CE_OI", "call_oi", "callOI"))
    pe_oi = _num(_get(row, "pe_oi", "PE_OI", "put_oi", "putOI"))

    ce_volume = _num(_get(row, "ce_volume", "CE_VOLUME", "call_volume", "callVolume"))
    pe_volume = _num(_get(row, "pe_volume", "PE_VOLUME", "put_volume", "putVolume"))

    return {
        "strike": strike,
        "ce_ltp": ce_ltp,
        "pe_ltp": pe_ltp,
        "ce_oi": ce_oi,
        "pe_oi": pe_oi,
        "ce_volume": ce_volume,
        "pe_volume": pe_volume,
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
    if not diffs:
        return default
    return int(min(diffs))


def _leg(row, action, opt_type):
    if not row:
        return None

    if opt_type == "CE":
        premium = row["ce_ltp"]
        oi = row["ce_oi"]
        volume = row["ce_volume"]
    else:
        premium = row["pe_ltp"]
        oi = row["pe_oi"]
        volume = row["pe_volume"]

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


def _calc_debit_spread(buy_leg, sell_leg):
    debit = round(buy_leg["premium"] - sell_leg["premium"], 2)
    width = abs(sell_leg["strike"] - buy_leg["strike"])
    max_profit = round(width - debit, 2)
    max_loss = max(debit, 0)
    if buy_leg["type"] == "CE":
        breakeven = round(buy_leg["strike"] + debit, 2)
    else:
        breakeven = round(buy_leg["strike"] - debit, 2)

    return {
        "net_debit": debit,
        "net_credit": 0,
        "max_profit": max_profit,
        "max_loss": max_loss,
        "breakeven": breakeven,
        "risk_reward": round(max_profit / max_loss, 2) if max_loss else None
    }


def _calc_credit_spread(sell_leg, buy_leg):
    credit = round(sell_leg["premium"] - buy_leg["premium"], 2)
    width = abs(sell_leg["strike"] - buy_leg["strike"])
    max_profit = max(credit, 0)
    max_loss = round(width - credit, 2)
    if sell_leg["type"] == "PE":
        breakeven = round(sell_leg["strike"] - credit, 2)
    else:
        breakeven = round(sell_leg["strike"] + credit, 2)

    return {
        "net_debit": 0,
        "net_credit": credit,
        "max_profit": max_profit,
        "max_loss": max_loss,
        "breakeven": breakeven,
        "risk_reward": round(max_profit / max_loss, 2) if max_loss else None
    }


def _calc_long(leg):
    premium = leg["premium"]
    if leg["type"] == "CE":
        breakeven = round(leg["strike"] + premium, 2)
    else:
        breakeven = round(leg["strike"] - premium, 2)

    return {
        "net_debit": premium,
        "net_credit": 0,
        "max_profit": "Open",
        "max_loss": premium,
        "breakeven": breakeven,
        "risk_reward": "Open"
    }


def build_live_option_legs(strategy_name, analytics):
    chain = analytics.get("chain") or []
    rows, by_strike = _chain_map(chain)

    if not rows:
        return {
            "status": "error",
            "reason": "Live option chain is not available.",
            "strategy": strategy_name,
            "legs": []
        }

    spot = _num(analytics.get("spot") or analytics.get("underlying_value"))
    atm = analytics.get("atm") or _nearest_strike(rows, spot)
    atm = _nearest_strike(rows, _num(atm))
    step = _step(rows)

    if not atm:
        return {
            "status": "error",
            "reason": "ATM strike could not be resolved from option chain.",
            "strategy": strategy_name,
            "legs": []
        }

    expiry = _expiry(analytics)
    name = (strategy_name or "").lower()

    legs = []
    calc = {}

    if "long call" in name:
        buy = _leg(by_strike.get(atm), "BUY", "CE")
        legs = [buy]
        calc = _calc_long(buy)

    elif "long put" in name:
        buy = _leg(by_strike.get(atm), "BUY", "PE")
        legs = [buy]
        calc = _calc_long(buy)

    elif "bull call" in name:
        buy_strike = atm
        sell_strike = _nearest_strike(rows, atm + step)
        buy = _leg(by_strike.get(buy_strike), "BUY", "CE")
        sell = _leg(by_strike.get(sell_strike), "SELL", "CE")
        legs = [buy, sell]
        calc = _calc_debit_spread(buy, sell)

    elif "bear put" in name:
        buy_strike = atm
        sell_strike = _nearest_strike(rows, atm - step)
        buy = _leg(by_strike.get(buy_strike), "BUY", "PE")
        sell = _leg(by_strike.get(sell_strike), "SELL", "PE")
        legs = [buy, sell]
        calc = _calc_debit_spread(buy, sell)

    elif "bull put" in name:
        sell_strike = _nearest_strike(rows, atm - step)
        buy_strike = _nearest_strike(rows, atm - (2 * step))
        sell = _leg(by_strike.get(sell_strike), "SELL", "PE")
        buy = _leg(by_strike.get(buy_strike), "BUY", "PE")
        legs = [sell, buy]
        calc = _calc_credit_spread(sell, buy)

    elif "bear call" in name:
        sell_strike = _nearest_strike(rows, atm + step)
        buy_strike = _nearest_strike(rows, atm + (2 * step))
        sell = _leg(by_strike.get(sell_strike), "SELL", "CE")
        buy = _leg(by_strike.get(buy_strike), "BUY", "CE")
        legs = [sell, buy]
        calc = _calc_credit_spread(sell, buy)

    elif "iron condor" in name:
        sell_pe_strike = _nearest_strike(rows, atm - step)
        buy_pe_strike = _nearest_strike(rows, atm - (2 * step))
        sell_ce_strike = _nearest_strike(rows, atm + step)
        buy_ce_strike = _nearest_strike(rows, atm + (2 * step))

        sell_pe = _leg(by_strike.get(sell_pe_strike), "SELL", "PE")
        buy_pe = _leg(by_strike.get(buy_pe_strike), "BUY", "PE")
        sell_ce = _leg(by_strike.get(sell_ce_strike), "SELL", "CE")
        buy_ce = _leg(by_strike.get(buy_ce_strike), "BUY", "CE")

        legs = [sell_pe, buy_pe, sell_ce, buy_ce]
        credit = round(sell_pe["premium"] + sell_ce["premium"] - buy_pe["premium"] - buy_ce["premium"], 2)
        width = step
        calc = {
            "net_credit": credit,
            "net_debit": 0,
            "max_profit": credit,
            "max_loss": round(width - credit, 2),
            "breakeven_lower": round(sell_pe["strike"] - credit, 2),
            "breakeven_upper": round(sell_ce["strike"] + credit, 2),
            "risk_reward": round(credit / (width - credit), 2) if width - credit else None
        }

    else:
        return {
            "status": "no_trade",
            "reason": "No option legs required for No Trade or unsupported strategy.",
            "strategy": strategy_name,
            "expiry": expiry,
            "legs": []
        }

    if any(l is None for l in legs):
        return {
            "status": "error",
            "reason": "One or more option legs could not be built from live chain.",
            "strategy": strategy_name,
            "expiry": expiry,
            "legs": []
        }

    return {
        "status": "ok",
        "strategy": strategy_name,
        "expiry": expiry,
        "atm": int(atm),
        "step": step,
        "legs": legs,
        "calculation": calc
    }
