from .scoring_config import *
from .score_utils import safe_score, clamp, institutional_grade, trade_quality

class InstitutionalScoreEngine:
    def calculate(self, trend, momentum, structure, vwap, option_chain, liquidity):
        comps = {
            "trend": safe_score(trend),
            "momentum": safe_score(momentum),
            "structure": safe_score(structure),
            "vwap": safe_score(vwap),
            "option_chain": safe_score(option_chain),
            "liquidity": safe_score(liquidity),
        }

        score = (
            comps["trend"]*TREND_WEIGHT +
            comps["momentum"]*MOMENTUM_WEIGHT +
            comps["structure"]*STRUCTURE_WEIGHT +
            comps["vwap"]*VWAP_WEIGHT +
            comps["option_chain"]*OPTION_CHAIN_WEIGHT +
            comps["liquidity"]*LIQUIDITY_WEIGHT
        ) / TOTAL_WEIGHT

        confidence = clamp(
            (
                abs(comps["trend"]-50)+
                abs(comps["momentum"]-50)+
                abs(comps["structure"]-50)+
                abs(comps["vwap"]-50)+
                abs(comps["option_chain"]-50)
            )/5*2
        )

        score = round(score,2)
        return {
            "institutional_score": score,
            "institutional_grade": institutional_grade(score),
            "trade_quality": trade_quality(score),
            "engine_confidence": round(confidence,2),
            "component_scores": comps
        }
