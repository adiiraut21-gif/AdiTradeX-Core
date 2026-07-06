
from .final_strategy_selector import final_strategy_selector
from .execution_summary import build_execution_summary

def build_strategy_lab(strategies, market_snapshot=None):
    final = final_strategy_selector(strategies, market_snapshot)
    summary = build_execution_summary(final)
    return {
        "final": final,
        "summary": summary,
        "status": final["verdict"]
    }
