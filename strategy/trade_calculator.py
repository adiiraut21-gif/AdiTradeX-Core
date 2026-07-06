def calculate_trade(entry_buy,entry_sell=0,lots=1):
    debit=max(entry_buy-entry_sell,0)
    credit=max(entry_sell-entry_buy,0)
    return {"net_debit":debit,"net_credit":credit,
            "max_loss":debit if debit else 100-credit,
            "max_profit":"Variable" if debit else credit,
            "breakeven":"Calculated at execution"}