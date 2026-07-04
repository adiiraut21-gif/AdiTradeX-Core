def generate_summary(analytics):
    underlying = analytics["underlying"]
    spot = analytics["spot"]
    pcr = analytics["pcr"]
    support = analytics["support"]
    resistance = analytics["resistance"]
    max_pain = analytics["max_pain"]
    bias = analytics["institutional_bias"]
    confidence = analytics["confidence"]

    parts = [
        f"{underlying} is trading near {spot}.",
        f"Primary support is around {support} and resistance is around {resistance}.",
        f"PCR is {pcr}, while Max Pain is near {max_pain}.",
        f"Institutional bias is {bias} with {confidence}% confidence."
    ]

    if bias == "Bullish":
        parts.append("Buy-on-dips structure is preferred unless support breaks decisively.")
    elif bias == "Bearish":
        parts.append("Sell-on-rise or bearish spread structure is preferred unless resistance is reclaimed.")
    else:
        parts.append("Market is balanced; avoid forcing directional trades.")

    return " ".join(parts)
