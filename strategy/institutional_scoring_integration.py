from analytics.service import analyze_underlying
from technical_pro.service import get_technical_intelligence_snapshot

from .institutional_score import InstitutionalScoreEngine
from .market_regime import detect_market_regime
from .probability_engine import build_probability
from .liquidity_engine import liquidity_score
from .ev_engine import expected_value_score
from .risk_classification import risk_classification
from .strategy_readiness import strategy_readiness
from .trade_quality_engine import trade_quality_engine
from .evidence_engine import build_evidence
from .decision_matrix import build_decision_matrix, weighted_matrix_score
from .score_explainer import explain_score
from .capital_preservation import capital_preservation_filter


SCORING_TIMEFRAMES = ["day", "75m", "15m", "5m"]


def _option_chain_score(analytics):
    pcr = analytics.get("pcr") or 1
    trade_quality = analytics.get("trade_quality") or 50

    if 0.95 <= pcr <= 1.20:
        pcr_score = 65
    elif 1.20 < pcr <= 1.45:
        pcr_score = 75
    elif 0.80 <= pcr < 0.95:
        pcr_score = 48
    elif pcr > 1.45:
        pcr_score = 58
    elif pcr < 0.80:
        pcr_score = 38
    else:
        pcr_score = 50

    return round((pcr_score * 0.45) + (trade_quality * 0.55), 2)


def build_institutional_scoring_summary(underlying="nifty"):
    analytics = analyze_underlying(underlying)
    technical = get_technical_intelligence_snapshot(underlying, timeframes=SCORING_TIMEFRAMES)

    trend = technical.get("trend", {}).get("average_trend_score", 50)
    momentum = technical.get("momentum", {}).get("average_momentum_score", 50)
    structure = technical.get("structure", {}).get("average_structure_score", 50)
    vwap = technical.get("vwap", {}).get("average_vwap_score", 50)
    option_chain = _option_chain_score(analytics)
    liquidity = liquidity_score()["liquidity_score"]

    base = InstitutionalScoreEngine().calculate(
        trend=trend,
        momentum=momentum,
        structure=structure,
        vwap=vwap,
        option_chain=option_chain,
        liquidity=liquidity
    )

    component_scores = {
        **base["component_scores"],
        "volatility": round(100 - (analytics.get("range_probability") or 50) + 20, 2)
    }

    regime = detect_market_regime(trend, momentum, structure, vwap)
    probability = build_probability(regime["regime_strength"])
    dominant_probability = max(
        probability["bull_probability"],
        probability["bear_probability"],
        probability["neutral_probability"]
    )

    ev = expected_value_score(
        base["institutional_score"],
        base["engine_confidence"],
        dominant_probability
    )

    risk = risk_classification(
        base["institutional_score"],
        base["engine_confidence"],
        ev["ev_score"]
    )

    readiness = strategy_readiness(
        base["institutional_score"],
        ev["ev_score"],
        risk["risk_level"]
    )

    trade_quality = trade_quality_engine(
        base["institutional_score"],
        ev["ev_score"]
    )

    evidence = build_evidence(component_scores, regime, probability)
    matrix = build_decision_matrix(component_scores, regime, probability)
    matrix_score = weighted_matrix_score(matrix)
    explainer = explain_score(
        base["institutional_score"],
        base["institutional_grade"],
        evidence,
        matrix
    )

    preservation = capital_preservation_filter(
        base["institutional_score"],
        base["engine_confidence"],
        ev["ev_score"],
        risk["risk_level"]
    )

    return {
        "underlying": analytics.get("underlying"),
        "spot": analytics.get("spot"),
        "atm": analytics.get("atm"),
        "expiry": analytics.get("expiry"),
        "pcr": analytics.get("pcr"),
        "support": analytics.get("support"),
        "resistance": analytics.get("resistance"),
        "max_pain": analytics.get("max_pain"),

        "institutional_score": base["institutional_score"],
        "institutional_grade": base["institutional_grade"],
        "engine_confidence": base["engine_confidence"],
        "trade_quality": trade_quality,
        "component_scores": component_scores,

        "market_regime": regime,
        "probability": probability,
        "expected_value": ev,
        "risk": risk,
        "strategy_readiness": readiness,
        "capital_preservation": preservation,

        "evidence": evidence,
        "decision_matrix": matrix,
        "decision_matrix_score": matrix_score,
        "explainer": explainer,

        "technical_bias": technical.get("technical_bias"),
        "technical_score": technical.get("technical_score"),
        "technical_commentary": {
            "trend": technical.get("trend_commentary"),
            "momentum": technical.get("momentum_commentary"),
            "vwap": technical.get("vwap_commentary"),
            "structure": technical.get("structure_commentary")
        },
        "analytics_summary": analytics.get("summary")
    }
