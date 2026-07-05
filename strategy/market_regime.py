from .score_utils import safe_score

def detect_market_regime(trend,momentum,structure,vwap):
    vals=[safe_score(x) for x in (trend,momentum,structure,vwap)]
    avg=sum(vals)/4
    align=sum(v>=60 for v in vals)
    if avg>=80 and align>=3: regime="Strong Bull"
    elif avg>=65: regime="Bull"
    elif avg<=35 and align<=1: regime="Strong Bear"
    elif avg<=45: regime="Bear"
    else: regime="Neutral"
    return {"regime":regime,"regime_strength":round(avg,2),"alignment":align}
