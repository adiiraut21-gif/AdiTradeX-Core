def top_oi_levels(chain, side="ce", count=3):
    key = "ce_oi" if side == "ce" else "pe_oi"
    rows = sorted(chain, key=lambda r: r.get(key) or 0, reverse=True)
    return [
        {
            "strike": r["strike"],
            "oi": r.get(key) or 0,
            "ltp": r.get("ce_ltp") if side == "ce" else r.get("pe_ltp")
        }
        for r in rows[:count]
    ]

def oi_concentration(chain):
    total_ce = sum(r.get("ce_oi") or 0 for r in chain)
    total_pe = sum(r.get("pe_oi") or 0 for r in chain)
    total = total_ce + total_pe

    if total == 0:
        return {
            "total_ce_oi": 0,
            "total_pe_oi": 0,
            "ce_share": None,
            "pe_share": None
        }

    return {
        "total_ce_oi": total_ce,
        "total_pe_oi": total_pe,
        "ce_share": round((total_ce / total) * 100, 2),
        "pe_share": round((total_pe / total) * 100, 2)
    }

def atm_oi(chain):
    atm = next((r for r in chain if r.get("is_atm")), None)
    if not atm:
        return None
    ce = atm.get("ce_oi") or 0
    pe = atm.get("pe_oi") or 0
    pcr = round(pe / ce, 2) if ce else None
    return {
        "strike": atm["strike"],
        "ce_oi": ce,
        "pe_oi": pe,
        "atm_pcr": pcr
    }
