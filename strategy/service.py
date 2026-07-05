from analytics.service import analyze_underlying
from technical.service import analyze_technical
from strategy.payoff import (
    long_call,
    long_put,
    bull_call_spread,
    bear_put_spread,
    bull_put_credit_spread,
    bear_call_credit_spread
)
from strategy.scorer import score_strategy, no_trade_strategy

STEP_MAP = {
    "NIFTY": 50,
    "BANKNIFTY": 100,
    "FINNIFTY": 50,
    "MIDCPNIFTY": 25
}

def build_strategy_decision(underlying="nifty", interval="15m"):
    analytics = analyze_underlying(underlying)
    technical = analyze_technical(underlying, interval)

    chain = analytics["chain"]
    atm = analytics["atm"]
    step = STEP_MAP.get(analytics["underlying"], 50)

    candidates = [
        long_call(chain, atm),
        long_put(chain, atm),
        bull_call_spread(chain, atm, step),
        bear_put_spread(chain, atm, step),
        bull_put_credit_spread(chain, atm, step),
        bear_call_credit_spread(chain, atm, step),
    ]

    scored = []
    for candidate in candidates:
        if candidate:
            scored.append(score_strategy(candidate, analytics, technical))

    scored.append(no_trade_strategy(analytics, technical))
    scored = sorted(scored, key=lambda x: x["score"], reverse=True)

    best = scored[0]
    institutional_grade = "YES" if best["score"] >= 75 and best["name"] != "No Trade" else "NO"

    return {
        "underlying": analytics["underlying"],
        "spot": analytics["spot"],
        "atm": analytics["atm"],
        "expiry": analytics["expiry"],
        "interval": interval,
        "institutional_bias": analytics["institutional_bias"],
        "technical_bias": technical["technical_bias"],
        "trade_quality": analytics["trade_quality"],
        "technical_score": technical["scores"]["technical_score"],
        "support": analytics["support"],
        "resistance": analytics["resistance"],
        "pcr": analytics["pcr"],
        "max_pain": analytics["max_pain"],
        "strategies": scored,
        "recommended_strategy": best,
        "institutional_grade": institutional_grade,
        "final_verdict": final_verdict(best, institutional_grade),
        "analytics_summary": analytics["summary"],
        "technical_summary": technical["summary"]
    }

def final_verdict(best, institutional_grade):
    if best["name"] == "No Trade":
        return "NO TRADE. Capital preservation mode is preferred because risk-adjusted setup quality is not strong enough."

    if institutional_grade == "YES":
        return f"{best['name']} is preferred. It has the strongest combined options + technical EV score."

    return f"{best['name']} ranks highest, but setup is not institutional grade yet. Prefer paper tracking or wait for confirmation."
