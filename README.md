# AdiTradeX 6.2B — Position Intelligence inside Strategy Lab

## Add
- position/
- strategy/position_intelligence_bridge.py
- templates/position_intelligence_panel.html

## Manual integration needed — no app.py changes

### 1) Edit strategy/service.py

Add import near top:

```python
from strategy.position_intelligence_bridge import get_strategy_lab_position_intelligence
```

Inside `build_strategy_decision()`, before the final return:

```python
position_intelligence = get_strategy_lab_position_intelligence()
```

Add this key to the returned dictionary:

```python
"position_intelligence": position_intelligence,
```

### 2) Edit templates/strategy_dashboard.html

Add this where you want the Position Intelligence section to appear:

```jinja2
{% include "position_intelligence_panel.html" %}
```

Recommended position: after Top 3 Strategy Option Legs and before Institutional Scoring.

## Why this package is safe
- No app.py changes.
- No new routes.
- Uses existing Strategy Lab page.
- If Zerodha position fetch fails, panel shows error without breaking Strategy Lab.
