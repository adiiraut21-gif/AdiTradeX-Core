def trend_alignment(trend,momentum,structure,vwap):
    return [{"component":n,"aligned":v>=60,"score":v} for n,v in [("Trend",trend),("Momentum",momentum),("Structure",structure),("VWAP",vwap)]]
