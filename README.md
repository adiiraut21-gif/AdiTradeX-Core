# AdiTradeX Milestone 2 - AdiStrike v5.0 Institutional UI

This release upgrades AdiTradeX Core into an institutional terminal-style interface.

## Includes

- Zerodha authentication
- Session storage
- Live index market data
- Market data API endpoints
- AdiStrike AlphaX v5.0-style dashboard
- Terminal-style sidebar
- Dark institutional UI
- System console
- Read-only mode

## Main URLs

- `/` login page
- `/dashboard` main institutional terminal
- `/market/dashboard` live market dashboard
- `/market/indices` JSON quotes
- `/market/quote/nifty`
- `/market/quote/banknifty`
- `/market/snapshots`
- `/status`
- `/profile`

## Deployment

Upload extracted files and folders to GitHub and redeploy Render.

Required Render environment variables:

- `KITE_API_KEY`
- `KITE_API_SECRET`
- `FLASK_SECRET_KEY`
- `LOG_LEVEL`

Redirect URL:

`https://aditradex-core.onrender.com/zerodha/callback`

## Safety

This version is read-only. It does not place, modify, or cancel orders.
