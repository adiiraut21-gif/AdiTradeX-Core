from analytics.scoring import clamp

def breakout_probability(spot, resistance, pcr, bull_score):
    if not resistance:
        return 50
    distance = max(resistance - spot, 0)
    distance_penalty = min(distance / 5, 25)
    pcr_boost = 8 if pcr and pcr > 1 else -6 if pcr and pcr < 0.8 else 0
    return round(clamp(bull_score - distance_penalty + pcr_boost), 2)

def breakdown_probability(spot, support, pcr, bear_score):
    if not support:
        return 50
    distance = max(spot - support, 0)
    distance_penalty = min(distance / 5, 25)
    pcr_boost = 8 if pcr and pcr < 0.8 else -6 if pcr and pcr > 1.15 else 0
    return round(clamp(bear_score - distance_penalty + pcr_boost), 2)

def range_probability(bull_breakout, bear_breakdown):
    return round(clamp(100 - max(bull_breakout, bear_breakdown)), 2)
