
def rank_strategies(strategies):
    ranked=[]
    for s in strategies:
        score=(
            s.get("ev_score",0)*0.30+
            s.get("pop",0)*0.20+
            s.get("risk_reward",0)*0.15+
            s.get("capital_efficiency",0)*0.10+
            s.get("greek_score",0)*0.10+
            s.get("liquidity_score",0)*0.05+
            s.get("institutional_score",0)*0.10
        )
        x=s.copy()
        x["ranking_score"]=round(score,2)
        ranked.append(x)
    return sorted(ranked,key=lambda x:x["ranking_score"],reverse=True)
