from .score_utils import clamp

def expected_value_score(institutional_score, engine_confidence, dominant_probability):
    score = round(
        institutional_score * 0.45 +
        engine_confidence * 0.35 +
        dominant_probability * 0.20,
        2
    )

    if score >= 85:
        label = "High Positive EV"
    elif score >= 75:
        label = "Positive EV"
    elif score >= 65:
        label = "Moderate EV"
    elif score >= 55:
        label = "Weak EV"
    else:
        label = "Negative / No Trade EV"

    return {
        "ev_score": clamp(score),
        "ev_label": label
    }
