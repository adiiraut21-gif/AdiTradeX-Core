def _score_liquidity(buy_leg, sell_leg):
    buy_liq = min((buy_leg.get("oi", 0) / 100000) * 50 + (buy_leg.get("volume", 0) / 10000) * 50, 100)
    sell_liq = min((sell_leg.get("oi", 0) / 100000) * 50 + (sell_leg.get("volume", 0) / 10000) * 50, 100)
    return round((buy_liq + sell_liq) / 2, 2)


def _make_leg(row, action, opt_type):
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


def _score_debit_spread(buy_leg, sell_leg, spot, direction):
    width = abs(sell_leg["strike"] - buy_leg["strike"])
    debit = round(buy_leg["premium"] - sell_leg["premium"], 2)

    if debit <= 0 or width <= 0:
        return None

    max_profit = round(width - debit, 2)
    max_loss = debit
    rr = round(max_profit / max_loss, 2) if max_loss else 0

    breakeven = round(buy_leg["strike"] + debit, 2) if direction == "bull" else round(buy_leg["strike"] - debit, 2)

    liq = _score_liquidity(buy_leg, sell_leg)
    rr_score = min(rr * 30, 100)
    debit_score = max(0, 100 - (debit / width) * 100)
    safety_score = max(0, 100 - abs(breakeven - spot) / spot * 1000) if spot else 50

    final_score = round(rr_score * 0.35 + debit_score * 0.25 + liq * 0.25 + safety_score * 0.15, 2)

    return {
        "score": final_score,
        "width": width,
        "net_debit": debit,
        "net_credit": 0,
        "max_profit": max_profit,
        "max_loss": max_loss,
        "breakeven": breakeven,
        "risk_reward": rr,
        "liquidity_score": liq,
        "reason": "Dynamic optimizer selected best debit spread using RR, debit quality, liquidity and breakeven safety."
    }


def _score_credit_spread(sell_leg, buy_leg, spot, direction):
    width = abs(sell_leg["strike"] - buy_leg["strike"])
    credit = round(sell_leg["premium"] - buy_leg["premium"], 2)

    if credit <= 0 or width <= 0:
        return None

    max_profit = credit
    max_loss = round(width - credit, 2)
    rr = round(max_profit / max_loss, 2) if max_loss else 0

    breakeven = round(sell_leg["strike"] - credit, 2) if direction == "bull" else round(sell_leg["strike"] + credit, 2)

    liq = _score_liquidity(sell_leg, buy_leg)
    credit_score = min((credit / width) * 300, 100)
    rr_score = min(rr * 60, 100)

    if spot:
        safety_score = max(0, (spot - breakeven) / spot * 1000) if direction == "bull" else max(0, (breakeven - spot) / spot * 1000)
        safety_score = min(safety_score, 100)
    else:
        safety_score = 50

    final_score = round(credit_score * 0.35 + rr_score * 0.20 + liq * 0.25 + safety_score * 0.20, 2)

    return {
        "score": final_score,
        "width": width,
        "net_debit": 0,
        "net_credit": credit,
        "max_profit": max_profit,
        "max_loss": max_loss,
        "breakeven": breakeven,
        "risk_reward": rr,
        "liquidity_score": liq,
        "reason": "Dynamic optimizer selected best credit spread using credit quality, safety, liquidity and risk."
    }


def _best(candidates):
    if not candidates:
        return None
    ranked = sorted(candidates, key=lambda x: x["calculation"]["score"], reverse=True)
    best = ranked[0]
    best["candidate_count"] = len(ranked)
    best["all_candidates"] = ranked[:10]
    return best


def optimize_debit_spread(rows, by_strike, atm, step, spot, opt_type, direction, max_width_steps=4):
    candidates = []
    for i in range(1, max_width_steps + 1):
        buy_strike = atm
        sell_strike = atm + (step * i) if direction == "bull" else atm - (step * i)

        buy_row = by_strike.get(buy_strike)
        sell_row = by_strike.get(sell_strike)

        if not buy_row or not sell_row:
            continue

        buy_leg = _make_leg(buy_row, "BUY", opt_type)
        sell_leg = _make_leg(sell_row, "SELL", opt_type)
        calc = _score_debit_spread(buy_leg, sell_leg, spot, direction)

        if calc:
            candidates.append({"legs": [buy_leg, sell_leg], "calculation": calc})

    return _best(candidates)


def optimize_credit_spread(rows, by_strike, atm, step, spot, opt_type, direction, max_width_steps=4):
    candidates = []
    for i in range(1, max_width_steps + 1):
        if direction == "bull":
            sell_strike = atm - step
            buy_strike = sell_strike - (step * i)
        else:
            sell_strike = atm + step
            buy_strike = sell_strike + (step * i)

        sell_row = by_strike.get(sell_strike)
        buy_row = by_strike.get(buy_strike)

        if not sell_row or not buy_row:
            continue

        sell_leg = _make_leg(sell_row, "SELL", opt_type)
        buy_leg = _make_leg(buy_row, "BUY", opt_type)
        calc = _score_credit_spread(sell_leg, buy_leg, spot, direction)

        if calc:
            candidates.append({"legs": [sell_leg, buy_leg], "calculation": calc})

    return _best(candidates)
