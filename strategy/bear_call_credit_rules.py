from .strategy_rule_utils import score_from_conditions, build_result

def evaluate_bear_call_credit_spread(ctx):
    score = score_from_conditions(55,
        boosts=[(ctx["institutional_score"] >= 70, 8), (ctx["bear_probability"] >= 55, 10),
                (ctx["regime"] in ["Bear", "Range", "Neutral"], 10),
                (ctx["neutral_probability"] >= 45, 8), (ctx["supportive_option_chain"], 8)],
        penalties=[(ctx["bull_probability"] >= 65, 20), (ctx["regime"] == "Strong Bull", 25),
                   (ctx["capital_action"] == "NO TRADE", 30)])
    return build_result("Bear Call Credit Spread", score >= 68, score, ctx["engine_confidence"], ctx["ev_label"], "Medium",
        "Works when market is bearish or range-bound below resistance.",
        "Upside risk or bullish probability is too high.")
