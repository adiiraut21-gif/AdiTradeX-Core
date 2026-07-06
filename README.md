# AdiTradeX 6.1C-5B — Top 3 Strategy Option Legs

## Add

- strategy/top_strategy_leg_builder.py

## Replace

- strategy/service.py
- templates/strategy_dashboard.html

## What this fixes

Earlier, when capital filter showed NO TRADE, the best strategy was overwritten and option legs were not displayed.

Now:
- Best Available Strategy is preserved.
- Execution Status is shown separately.
- Top 3 ranked strategies receive live option legs.
- NO TRADE blocks execution, but does not hide strategy analysis.

No app.py changes.
