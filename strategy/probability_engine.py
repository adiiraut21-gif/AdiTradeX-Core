from .score_utils import clamp
def build_probability(regime_strength):
    bull=clamp(50+(regime_strength-50))
    bear=clamp(100-bull)
    neutral=clamp(100-abs(bull-bear)-20)
    bias="Bullish" if bull>bear else "Bearish" if bear>bull else "Neutral"
    return {"bull_probability":round(bull,2),"bear_probability":round(bear,2),"neutral_probability":round(neutral,2),"institutional_bias":bias}
