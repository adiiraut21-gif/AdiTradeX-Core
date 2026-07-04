def strongest_support(chain, spot, count=3):
    puts_below = [
        r for r in chain
        if r["strike"] <= spot and (r.get("pe_oi") or 0) > 0
    ]
    rows = sorted(puts_below, key=lambda r: r.get("pe_oi") or 0, reverse=True)
    return [{"strike": r["strike"], "oi": r.get("pe_oi") or 0} for r in rows[:count]]

def strongest_resistance(chain, spot, count=3):
    calls_above = [
        r for r in chain
        if r["strike"] >= spot and (r.get("ce_oi") or 0) > 0
    ]
    rows = sorted(calls_above, key=lambda r: r.get("ce_oi") or 0, reverse=True)
    return [{"strike": r["strike"], "oi": r.get("ce_oi") or 0} for r in rows[:count]]

def primary_support(supports):
    return supports[0]["strike"] if supports else None

def primary_resistance(resistances):
    return resistances[0]["strike"] if resistances else None
