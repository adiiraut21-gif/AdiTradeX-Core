
def build_execution_summary(final_result):
    if final_result["verdict"]=="NO TRADE":
        return {
            "headline":"Capital Preservation",
            "message":"No institutional-grade opportunity detected."
        }
    e=final_result["execution"]
    return {
        "headline":f"Execute {e['strategy']}",
        "expiry":e.get("expiry"),
        "buy_leg":e.get("buy_leg"),
        "sell_leg":e.get("sell_leg"),
        "confidence":e.get("confidence"),
        "ev_score":e.get("ev_score")
    }
