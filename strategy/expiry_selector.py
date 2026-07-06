def select_expiry(regime, holding_days=1, event_risk=False):
    if event_risk: return {"expiry":"Next Weekly","reason":"Avoid event theta risk"}
    if holding_days<=2: return {"expiry":"Current Weekly","reason":"Short-term trade"}
    if holding_days<=7: return {"expiry":"Next Weekly","reason":"Swing horizon"}
    return {"expiry":"Monthly","reason":"Longer holding period"}