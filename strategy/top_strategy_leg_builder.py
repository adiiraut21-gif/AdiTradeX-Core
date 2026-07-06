from strategy.live_option_leg_wiring import build_live_option_legs

def attach_option_legs_to_top_strategies(strategies, analytics, top_n=3):
    enriched = []
    ranked = sorted(strategies, key=lambda x: x.get("score", 0), reverse=True)

    for index, strategy in enumerate(ranked):
        item = strategy.copy()
        item["rank"] = index + 1

        if index < top_n and item.get("name") != "No Trade":
            legs = build_live_option_legs(item.get("name"), analytics)
            item["live_option_trade"] = legs

            if legs.get("status") == "ok":
                item["expiry"] = legs.get("expiry")
                item["legs"] = legs.get("legs", [])
                item["calculation"] = legs.get("calculation", {})
                item["leg_status"] = "AVAILABLE"
            else:
                item["legs"] = []
                item["calculation"] = {}
                item["leg_status"] = "NOT AVAILABLE"
                item["leg_error"] = legs.get("reason")
        else:
            item["legs"] = []
            item["calculation"] = {}
            item["leg_status"] = "NOT REQUESTED"

        enriched.append(item)

    return enriched
