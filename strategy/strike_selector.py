def select_strike(strategy,bias,spot,step=50):
    atm=round(spot/step)*step
    if strategy in ["Long Call","Bull Call Spread"]:
        buy=atm; sell=atm+step if "Spread" in strategy else None
    elif strategy in ["Long Put","Bear Put Spread"]:
        buy=atm; sell=atm-step if "Spread" in strategy else None
    else:
        buy=atm; sell=None
    return {"atm":atm,"buy_strike":buy,"sell_strike":sell}