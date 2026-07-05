def find_row(chain, strike):
    return next((r for r in chain if r["strike"] == strike), None)

def safe_value(value):
    return value if value is not None else 0

def long_call(chain, atm):
    row = find_row(chain, atm)
    if not row:
        return None

    premium = safe_value(row.get("ce_ltp"))
    if premium <= 0:
        return None

    return {
        "name": "Long Call",
        "type": "Directional Option",
        "direction": "Bullish",
        "buy_leg": f"BUY {atm} CE",
        "premium": premium,
        "max_loss": premium,
        "max_profit": "Unlimited",
        "breakeven": round(atm + premium, 2),
        "risk_defined": True
    }

def long_put(chain, atm):
    row = find_row(chain, atm)
    if not row:
        return None

    premium = safe_value(row.get("pe_ltp"))
    if premium <= 0:
        return None

    return {
        "name": "Long Put",
        "type": "Directional Option",
        "direction": "Bearish",
        "buy_leg": f"BUY {atm} PE",
        "premium": premium,
        "max_loss": premium,
        "max_profit": "High",
        "breakeven": round(atm - premium, 2),
        "risk_defined": True
    }

def bull_call_spread(chain, atm, step):
    buy = find_row(chain, atm)
    sell = find_row(chain, atm + step)

    if not buy or not sell:
        return None

    buy_ltp = safe_value(buy.get("ce_ltp"))
    sell_ltp = safe_value(sell.get("ce_ltp"))
    debit = round(buy_ltp - sell_ltp, 2)

    if debit <= 0:
        return None

    return {
        "name": "Bull Call Spread",
        "type": "Debit Spread",
        "direction": "Bullish",
        "buy_leg": f"BUY {atm} CE",
        "sell_leg": f"SELL {atm + step} CE",
        "net_debit": debit,
        "max_profit": round(step - debit, 2),
        "max_loss": debit,
        "breakeven": round(atm + debit, 2),
        "risk_defined": True
    }

def bear_put_spread(chain, atm, step):
    buy = find_row(chain, atm)
    sell = find_row(chain, atm - step)

    if not buy or not sell:
        return None

    buy_ltp = safe_value(buy.get("pe_ltp"))
    sell_ltp = safe_value(sell.get("pe_ltp"))
    debit = round(buy_ltp - sell_ltp, 2)

    if debit <= 0:
        return None

    return {
        "name": "Bear Put Spread",
        "type": "Debit Spread",
        "direction": "Bearish",
        "buy_leg": f"BUY {atm} PE",
        "sell_leg": f"SELL {atm - step} PE",
        "net_debit": debit,
        "max_profit": round(step - debit, 2),
        "max_loss": debit,
        "breakeven": round(atm - debit, 2),
        "risk_defined": True
    }

def bull_put_credit_spread(chain, atm, step):
    sell = find_row(chain, atm - step)
    buy = find_row(chain, atm - (2 * step))

    if not buy or not sell:
        return None

    sell_ltp = safe_value(sell.get("pe_ltp"))
    buy_ltp = safe_value(buy.get("pe_ltp"))
    credit = round(sell_ltp - buy_ltp, 2)

    if credit <= 0:
        return None

    return {
        "name": "Bull Put Credit Spread",
        "type": "Credit Spread",
        "direction": "Bullish / Neutral",
        "sell_leg": f"SELL {atm - step} PE",
        "buy_leg": f"BUY {atm - (2 * step)} PE",
        "net_credit": credit,
        "max_profit": credit,
        "max_loss": round(step - credit, 2),
        "breakeven": round((atm - step) - credit, 2),
        "risk_defined": True
    }

def bear_call_credit_spread(chain, atm, step):
    sell = find_row(chain, atm + step)
    buy = find_row(chain, atm + (2 * step))

    if not buy or not sell:
        return None

    sell_ltp = safe_value(sell.get("ce_ltp"))
    buy_ltp = safe_value(buy.get("ce_ltp"))
    credit = round(sell_ltp - buy_ltp, 2)

    if credit <= 0:
        return None

    return {
        "name": "Bear Call Credit Spread",
        "type": "Credit Spread",
        "direction": "Bearish / Neutral",
        "sell_leg": f"SELL {atm + step} CE",
        "buy_leg": f"BUY {atm + (2 * step)} CE",
        "net_credit": credit,
        "max_profit": credit,
        "max_loss": round(step - credit, 2),
        "breakeven": round((atm + step) + credit, 2),
        "risk_defined": True
    }
