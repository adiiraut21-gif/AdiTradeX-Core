
from .best_strategy_selector import select_best_strategy

def final_strategy_selector(strategies, market_snapshot=None):
    result = select_best_strategy(strategies)
    if result["decision"] == "NO TRADE":
        return {
            "verdict":"NO TRADE",
            "recommended_strategy":None,
            "execution":"Stand aside and preserve capital.",
            "summary":result
        }
    best = result["best_strategy"]
    return {
        "verdict":"TRADE",
        "recommended_strategy":best,
        "execution":{
            "strategy":best.get("strategy_name"),
            "expiry":best.get("expiry","To be supplied by 6.1C-5"),
            "buy_leg":best.get("buy_leg"),
            "sell_leg":best.get("sell_leg"),
            "confidence":best.get("confidence"),
            "ev_score":best.get("ev_score"),
            "pop":best.get("pop"),
            "risk_reward":best.get("risk_reward")
        },
        "market_snapshot":market_snapshot or {},
        "summary":result
    }
