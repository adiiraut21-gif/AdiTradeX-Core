def liquidity_score(volume_score=75,spread_score=75):
    score=round(volume_score*0.7+spread_score*0.3,2)
    level="High" if score>=80 else "Normal" if score>=60 else "Low"
    return {"liquidity_score":score,"liquidity_level":level}
