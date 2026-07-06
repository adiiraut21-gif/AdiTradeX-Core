
def reject_strategy(strategy):
    reasons=[]
    if strategy.get("ev_score",0)<60: reasons.append("Low Expected Value")
    if strategy.get("pop",0)<55: reasons.append("Low Probability of Profit")
    if strategy.get("institutional_score",0)<70: reasons.append("Weak Institutional Score")
    if strategy.get("liquidity_score",100)<60: reasons.append("Poor Liquidity")
    return {"rejected":len(reasons)>0,"reasons":reasons}
