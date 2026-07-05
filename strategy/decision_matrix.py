def build_decision_matrix(component_scores, market_regime=None, probability=None):
    rows = [
        {
            "component": "Trend",
            "weight": 20,
            "score": component_scores.get("trend", 50),
            "reason": "Multi-timeframe trend alignment."
        },
        {
            "component": "Momentum",
            "weight": 15,
            "score": component_scores.get("momentum", 50),
            "reason": "RSI, MACD and momentum quality."
        },
        {
            "component": "Futures VWAP",
            "weight": 15,
            "score": component_scores.get("vwap", 50),
            "reason": "Index futures VWAP positioning and acceptance."
        },
        {
            "component": "Market Structure",
            "weight": 15,
            "score": component_scores.get("structure", 50),
            "reason": "Swing structure, BOS/CHOCH and liquidity context."
        },
        {
            "component": "Option Chain",
            "weight": 15,
            "score": component_scores.get("option_chain", 50),
            "reason": "PCR, support/resistance and option-chain quality."
        },
        {
            "component": "Liquidity",
            "weight": 10,
            "score": component_scores.get("liquidity", 50),
            "reason": "Execution quality and tradability."
        },
        {
            "component": "Volatility",
            "weight": 10,
            "score": component_scores.get("volatility", 50),
            "reason": "Volatility environment and range risk."
        }
    ]

    if market_regime:
        rows.append({
            "component": "Market Regime",
            "weight": 10,
            "score": market_regime.get("regime_strength", 50),
            "reason": market_regime.get("regime", "Neutral")
        })

    if probability:
        rows.append({
            "component": "Probability Edge",
            "weight": 10,
            "score": probability.get("dominant_probability", 50),
            "reason": probability.get("institutional_bias", "Neutral")
        })

    return rows


def weighted_matrix_score(matrix):
    total_weight = sum(row.get("weight", 0) for row in matrix)
    if total_weight == 0:
        return 50

    score = sum(row.get("score", 50) * row.get("weight", 0) for row in matrix) / total_weight
    return round(score, 2)
