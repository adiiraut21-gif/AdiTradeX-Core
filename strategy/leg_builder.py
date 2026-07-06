def build_legs(strategy,strikes,opt_type):
    b=strikes["buy_strike"]; s=strikes["sell_strike"]
    if strategy.startswith("Long"):
        return [{"action":"BUY","strike":b,"type":opt_type}]
    legs=[{"action":"BUY","strike":b,"type":opt_type}]
    if s: legs.append({"action":"SELL","strike":s,"type":opt_type})
    return legs