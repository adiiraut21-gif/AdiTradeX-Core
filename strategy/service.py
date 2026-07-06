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
from strategy.institutional_scoring_integration import build_institutional_scoring_summary
from strategy.live_option_leg_wiring import build_live_option_legs
from strategy.top_strategy_leg_builder import attach_option_legs_to_top_strategies

STEP_MAP = {
    "NIFTY": 50,
    "BANKNIFTY": 100,
    "FINNIFTY": 50,
    "MIDCPNIFTY": 25
}

def build_strategy_decision(underlying="nifty", interval="15m"):
    analytics = analyze_underlying(underlying)
    technical = analyze_technical(underlying, interval)
    institutional = build_institutional_scoring_summary(underlying)

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

    best_available_strategy = scored[0]

    execution_status = "APPROVED"
    execution_reason = "Strategy is approved for execution."

    if institutional["capital_preservation"]["action"] in ["WAIT", "NO TRADE"]:
        execution_status = "NOT APPROVED"
        execution_reason = institutional["capital_preservation"]["message"]

    top_strategies_with_legs = attach_option_legs_to_top_strategies(scored, analytics, top_n=3)

    recommended_strategy = best_available_strategy.copy()
    live_option_trade = build_live_option_legs(best_available_strategy.get("name"), analytics)

    if live_option_trade.get("status") == "ok":
        calc = live_option_trade.get("calculation", {})
        recommended_strategy["expiry"] = live_option_trade.get("expiry")
        recommended_strategy["legs"] = live_option_trade.get("legs")
        recommended_strategy["buy_leg"] = next((l["display"] for l in live_option_trade["legs"] if l["action"] == "BUY"), None)
        recommended_strategy["sell_leg"] = next((l["display"] for l in live_option_trade["legs"] if l["action"] == "SELL"), None)
        recommended_strategy["net_debit"] = calc.get("net_debit")
        recommended_strategy["net_credit"] = calc.get("net_credit")
        recommended_strategy["max_profit"] = calc.get("max_profit")
        recommended_strategy["max_loss"] = calc.get("max_loss")
        recommended_strategy["breakeven"] = calc.get("breakeven")
        recommended_strategy["breakeven_lower"] = calc.get("breakeven_lower")
        recommended_strategy["breakeven_upper"] = calc.get("breakeven_upper")
        recommended_strategy["risk_reward"] = calc.get("risk_reward")
    else:
        recommended_strategy["legs"] = []
        recommended_strategy["expiry"] = live_option_trade.get("expiry")
        recommended_strategy["leg_error"] = live_option_trade.get("reason")

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
        "top_strategies_with_legs": top_strategies_with_legs,
        "best_available_strategy": best_available_strategy,
        "recommended_strategy": recommended_strategy,
        "execution_status": execution_status,
        "execution_reason": execution_reason,
        "institutional_grade": "YES" if execution_status == "APPROVED" else "NO",
        "final_verdict": final_verdict(best_available_strategy, execution_status, execution_reason),
        "analytics_summary": analytics["summary"],
        "technical_summary": technical["summary"],
        "institutional_scoring": institutional,
        "live_option_trade": live_option_trade
    }

def final_verdict(best, execution_status, execution_reason):
    if execution_status == "NOT APPROVED":
        return f"{best['name']} is the best available strategy, but execution is NOT APPROVED. {execution_reason}"

    return f"{best['name']} is approved. It has the strongest combined options + technical EV score."
