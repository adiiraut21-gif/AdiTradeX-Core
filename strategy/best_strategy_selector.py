
from .strategy_rejection_engine import reject_strategy
from .strategy_ranking_engine import rank_strategies

def select_best_strategy(strategies):
    accepted=[]
    rejected=[]
    for s in strategies:
        r=reject_strategy(s)
        s["rejection"]=r
        if r["rejected"]:
            rejected.append(s)
        else:
            accepted.append(s)
    ranked=rank_strategies(accepted)
    if not ranked:
        return {
            "decision":"NO TRADE",
            "reason":"All strategies rejected",
            "accepted":[],
            "rejected":rejected
        }
    return {
        "decision":ranked[0]["strategy_name"],
        "best_strategy":ranked[0],
        "accepted":ranked,
        "rejected":rejected
    }
