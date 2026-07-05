def trade_quality_engine(institutional_score, ev_score):
    combined = round((institutional_score * 0.6) + (ev_score * 0.4), 2)

    if combined >= 90:
        quality = "Institutional Grade"
    elif combined >= 80:
        quality = "High Quality"
    elif combined >= 70:
        quality = "Watchlist Quality"
    elif combined >= 60:
        quality = "Low Edge"
    else:
        quality = "Reject"

    return {
        "trade_quality_score": combined,
        "trade_quality_label": quality
    }
