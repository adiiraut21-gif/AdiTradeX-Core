from .scoring_config import *

def clamp(v, low=MIN_SCORE, high=MAX_SCORE):
    return max(low, min(high, float(v)))

def safe_score(v, default=DEFAULT_SCORE):
    try:
        return clamp(v)
    except Exception:
        return default

def institutional_grade(score):
    if score >= GRADE_A_PLUS: return "A+"
    if score >= GRADE_A: return "A"
    if score >= GRADE_B: return "B"
    if score >= GRADE_C: return "C"
    return "Reject"

def trade_quality(score):
    if score >= QUALITY_INSTITUTIONAL: return "Institutional"
    if score >= QUALITY_HIGH: return "High Quality"
    if score >= QUALITY_WATCHLIST: return "Watchlist"
    if score >= QUALITY_WEAK: return "Weak"
    return "Reject"
