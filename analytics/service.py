from options.service import build_option_chain
from analytics.oi_engine import top_oi_levels, oi_concentration, atm_oi
from analytics.support_resistance import strongest_support, strongest_resistance, primary_support, primary_resistance
from analytics.probability import breakout_probability, breakdown_probability, range_probability
from analytics.scoring import score_pcr, score_oi_bias, score_spot_position, grade
from analytics.summary import generate_summary

def analyze_underlying(underlying="nifty"):
    data = build_option_chain(underlying)
    chain = data["chain"]
    spot = data["spot"]
    pcr = data["pcr"]

    call_walls = top_oi_levels(chain, "ce", 5)
    put_bases = top_oi_levels(chain, "pe", 5)
    concentration = oi_concentration(chain)
    atm = atm_oi(chain)

    supports = strongest_support(chain, spot, 3)
    resistances = strongest_resistance(chain, spot, 3)
    support = primary_support(supports)
    resistance = primary_resistance(resistances)

    pcr_score = score_pcr(pcr)
    oi_score = score_oi_bias(data["total_put_oi"], data["total_call_oi"])
    position_score = score_spot_position(spot, support, resistance)

    bull_score = round((pcr_score * 0.35) + (oi_score * 0.45) + (position_score * 0.20), 2)
    bear_score = round(100 - bull_score, 2)

    if bull_score >= 62:
        bias = "Bullish"
    elif bear_score >= 62:
        bias = "Bearish"
    else:
        bias = "Neutral"

    confidence = round(max(bull_score, bear_score), 2)

    bull_breakout = breakout_probability(spot, resistance, pcr, bull_score)
    bear_breakdown = breakdown_probability(spot, support, pcr, bear_score)
    range_prob = range_probability(bull_breakout, bear_breakdown)

    trade_quality = round((confidence * 0.55) + (abs(bull_score - bear_score) * 0.45), 2)

    analytics = {
        "underlying": data["underlying"],
        "spot": spot,
        "atm": data["atm"],
        "expiry": data["expiry"],
        "pcr": pcr,
        "atm_pcr": atm.get("atm_pcr") if atm else None,
        "max_pain": data["max_pain"],
        "total_call_oi": data["total_call_oi"],
        "total_put_oi": data["total_put_oi"],
        "call_walls": call_walls,
        "put_bases": put_bases,
        "support_levels": supports,
        "resistance_levels": resistances,
        "support": support,
        "resistance": resistance,
        "oi_concentration": concentration,
        "atm_oi": atm,
        "bull_score": bull_score,
        "bear_score": bear_score,
        "neutral_score": round(100 - abs(bull_score - bear_score), 2),
        "institutional_bias": bias,
        "confidence": confidence,
        "trade_quality": trade_quality,
        "grade": grade(trade_quality),
        "bull_breakout_probability": bull_breakout,
        "bear_breakdown_probability": bear_breakdown,
        "range_probability": range_prob,
        "chain": chain
    }

    analytics["summary"] = generate_summary(analytics)
    return analytics
