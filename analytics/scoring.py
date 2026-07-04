def clamp(value, low=0, high=100):
    return max(low, min(high, value))

def score_pcr(pcr):
    if pcr is None:
        return 50
    if pcr < 0.65:
        return 25
    if pcr < 0.85:
        return 45
    if pcr <= 1.15:
        return 60
    if pcr <= 1.35:
        return 75
    return 65

def score_oi_bias(total_put_oi, total_call_oi):
    if not total_call_oi:
        return 50
    ratio = total_put_oi / total_call_oi
    return clamp(50 + (ratio - 1) * 35)

def score_spot_position(spot, support, resistance):
    if not support or not resistance or support == resistance:
        return 50
    pos = (spot - support) / (resistance - support)
    return clamp(pos * 100)

def grade(score):
    if score >= 85:
        return "A+"
    if score >= 75:
        return "A"
    if score >= 65:
        return "B"
    if score >= 50:
        return "C"
    return "D"
