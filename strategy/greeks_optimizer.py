def evaluate_greeks(delta,gamma,theta,vega):
    score=50
    if abs(delta)>=0.45: score+=15
    if gamma>0: score+=10
    if theta>-5: score+=10
    if vega>=0: score+=5
    return {"greek_score":min(score,100),"approved":score>=70}